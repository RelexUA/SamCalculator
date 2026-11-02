package com.example.samcalculator;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.DisplayCutout;
import android.view.View;
import android.view.Window;
import android.view.WindowInsets;
import android.view.WindowInsetsController;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;

import java.util.Locale;

/**
 * Тонкая обёртка: показывает тот же samcalculator.html (лежит в assets/index.html).
 * Настройки и история хранятся в localStorage страницы, внутри приложения.
 *
 * Полноэкранный режим (настройка в приложении): окно рисуется под системными панелями и
 * вырезом камеры, а страница получает их размеры и сама отодвигает от них кнопки.
 */
public class MainActivity extends Activity {
    private static final int FILE_REQUEST = 1;

    private WebView webView;
    private FrameLayout rootView;
    private ValueCallback<Uri[]> filePathCallback;
    private boolean fullscreen = false;
    private boolean lightBars = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        webView.setBackgroundColor(0xFF000000);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        // Подложка нужна, чтобы отступы под клавиатуру работали надёжно (у WebView они не всегда учитываются)
        rootView = new FrameLayout(this);
        rootView.setBackgroundColor(0xFF000000);
        rootView.addView(webView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(rootView);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);              // только для чтения своих assets
        s.setAllowContentAccess(false);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setTextZoom(100);                      // системный размер шрифта не ломает вёрстку
        s.setUserAgentString(s.getUserAgentString() + " SamCalcApp");

        webView.addJavascriptInterface(new Bridge(), "AndroidBridge");
        webView.setOnApplyWindowInsetsListener((v, insets) -> {
            handleInsets(insets);
            return insets;
        });

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            // Выбор картинки для фона
            @Override
            public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                                             FileChooserParams params) {
                if (filePathCallback != null) filePathCallback.onReceiveValue(null);
                filePathCallback = callback;
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("image/*");
                try {
                    startActivityForResult(Intent.createChooser(intent, null), FILE_REQUEST);
                } catch (Exception e) {
                    filePathCallback = null;
                    callback.onReceiveValue(null);
                    return false;
                }
                return true;
            }
        });

        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState);
        } else {
            webView.loadUrl("file:///android_asset/index.html");
        }
    }

    // ---- связь со страницей ----------------------------------------------------------
    public class Bridge {
        @JavascriptInterface
        public void setFullscreen(final boolean on) {
            runOnUiThread(() -> applyFullscreen(on));
        }

        @JavascriptInterface
        public void setIconFollowsTheme(final boolean on) {
            runOnUiThread(() -> {
                getSharedPreferences("icon", MODE_PRIVATE).edit().putBoolean("follow", on).apply();
                applyIcon();
            });
        }

        @JavascriptInterface
        public void setLightBars(final boolean light) {
            runOnUiThread(() -> {
                lightBars = light;
                applyBars();
            });
        }
    }

    // Иконка приложения: тёмная по умолчанию. Если включено "по теме телефона" и у телефона
    // светлая тема, включается вторая иконка. Приложение при этом не перезапускается.
    // Сменить иконку можно только пока приложение открыто, поэтому проверка идёт при запуске
    // и при смене темы, а лаунчер обновляет значок с небольшой задержкой.
    private void applyIcon() {
        boolean follow = getSharedPreferences("icon", MODE_PRIVATE).getBoolean("follow", false);
        boolean night = (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK)
                == Configuration.UI_MODE_NIGHT_YES;
        boolean light = follow && !night;
        setAlias("com.example.samcalculator.IconLight", light);
        setAlias("com.example.samcalculator.IconDark", !light);
    }

    private void setAlias(String name, boolean enable) {
        PackageManager pm = getPackageManager();
        ComponentName cn = new ComponentName(this, name);
        int want = enable ? PackageManager.COMPONENT_ENABLED_STATE_ENABLED
                          : PackageManager.COMPONENT_ENABLED_STATE_DISABLED;
        if (pm.getComponentEnabledSetting(cn) != want) {
            pm.setComponentEnabledSetting(cn, want, PackageManager.DONT_KILL_APP);
        }
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        applyIcon();
    }

    private void applyFullscreen(boolean on) {
        fullscreen = on;
        Window w = getWindow();
        if (Build.VERSION.SDK_INT >= 28) {
            WindowManager.LayoutParams lp = w.getAttributes();
            lp.layoutInDisplayCutoutMode = on
                    ? WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES
                    : WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_DEFAULT;
            w.setAttributes(lp);
        }
        if (Build.VERSION.SDK_INT >= 30) {
            w.setDecorFitsSystemWindows(!on);
        } else {
            View d = w.getDecorView();
            int mask = View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION;
            int f = d.getSystemUiVisibility();
            d.setSystemUiVisibility(on ? (f | mask) : (f & ~mask));
        }
        int barColor = on ? Color.TRANSPARENT : Color.BLACK;
        w.setStatusBarColor(barColor);
        w.setNavigationBarColor(barColor);
        if (Build.VERSION.SDK_INT >= 29) {
            w.setNavigationBarContrastEnforced(false);
            w.setStatusBarContrastEnforced(false);
        }
        applyBars();
        if (!on) {
            rootView.setPadding(0, 0, 0, 0);
            pushInsets(0, 0, 0, 0);
        }
        webView.requestApplyInsets();
    }

    // Тёмные значки на панелях, если приложение в светлой теме
    private void applyBars() {
        boolean light = fullscreen && lightBars;
        Window w = getWindow();
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController c = w.getInsetsController();
            if (c != null) {
                int m = WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                        | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(light ? m : 0, m);
            }
        } else {
            View d = w.getDecorView();
            int m = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            if (Build.VERSION.SDK_INT >= 26) m |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            int f = d.getSystemUiVisibility();
            d.setSystemUiVisibility(light ? (f | m) : (f & ~m));
        }
    }

    // Размеры системных панелей и выреза -> странице (в CSS-пикселях)
    private void handleInsets(WindowInsets insets) {
        if (!fullscreen) return;
        int t, r, b, l;
        int pad = 0;
        if (Build.VERSION.SDK_INT >= 30) {
            android.graphics.Insets bars = insets.getInsets(
                    WindowInsets.Type.systemBars() | WindowInsets.Type.displayCutout());
            android.graphics.Insets ime = insets.getInsets(WindowInsets.Type.ime());
            t = bars.top;
            r = bars.right;
            l = bars.left;
            b = bars.bottom;
            // Клавиатура: окно в этом режиме само не сжимается, поэтому поднимаем страницу сами
            if (ime.bottom > bars.bottom) {
                pad = ime.bottom;
                b = 0;
            }
        } else {
            t = insets.getSystemWindowInsetTop();
            r = insets.getSystemWindowInsetRight();
            l = insets.getSystemWindowInsetLeft();
            b = insets.getStableInsetBottom();
            int sys = insets.getSystemWindowInsetBottom();
            if (sys > b) {
                pad = sys;
                b = 0;
            }
            if (Build.VERSION.SDK_INT >= 28) {
                DisplayCutout dc = insets.getDisplayCutout();
                if (dc != null) {
                    t = Math.max(t, dc.getSafeInsetTop());
                    l = Math.max(l, dc.getSafeInsetLeft());
                    r = Math.max(r, dc.getSafeInsetRight());
                }
            }
        }
        rootView.setPadding(0, 0, 0, pad);
        pushInsets(t, r, b, l);
    }

    private void pushInsets(int t, int r, int b, int l) {
        float d = getResources().getDisplayMetrics().density;
        String js = String.format(Locale.US,
                "window.setInsets && window.setInsets(%.1f,%.1f,%.1f,%.1f)",
                t / d, r / d, b / d, l / d);
        webView.evaluateJavascript(js, null);
    }

    // ---- обычные обработчики -------------------------------------------------------------
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode == FILE_REQUEST && filePathCallback != null) {
            Uri[] result = null;
            if (resultCode == RESULT_OK && data != null && data.getData() != null) {
                result = new Uri[]{data.getData()};
            }
            filePathCallback.onReceiveValue(result);
            filePathCallback = null;
            return;
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    // «Назад» сначала закрывает открытую панель (история, настройки, конвертер), и только потом выходит
    @Override
    public void onBackPressed() {
        webView.evaluateJavascript(
                "(window.androidBack && window.androidBack()) === true",
                value -> {
                    if (!"true".equals(value)) {
                        finish();
                    }
                });
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }

    @Override
    protected void onPause() {
        super.onPause();
        webView.onPause();
        webView.pauseTimers();   // в фоне страница полностью спит, батарея не тратится
    }

    @Override
    protected void onResume() {
        super.onResume();
        webView.onResume();
        webView.resumeTimers();
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
