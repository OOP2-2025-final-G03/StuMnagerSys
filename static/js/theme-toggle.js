// テーマ切替機能

document.addEventListener('DOMContentLoaded', () => {
    const toggleSwitch = document.querySelector('#checkbox-theme');
    const currentTheme = localStorage.getItem('theme');
    
    // 初期化テーマ設定
    if (currentTheme) {
        document.documentElement.setAttribute('data-theme', currentTheme);
        if (currentTheme === 'dark') {
            toggleSwitch.checked = true;
        }
    } else {
        // ユーザーのシステム設定を考慮
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
            toggleSwitch.checked = true;
        }
    }

    // テーマ切替イベントリスナー
    toggleSwitch.addEventListener('change', function(e) {
        if (e.target.checked) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    });
});