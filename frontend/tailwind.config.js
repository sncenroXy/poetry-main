/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        // Apple + 国风融合色板
        primary: '#c8851a',        // 赤金 - 主色调/CTA
        'primary-light': '#f5d68a',
        'primary-bg': 'rgba(200, 133, 26, 0.08)',
        accent: '#e54d42',         // 朱砂 - 强调/错误
        'accent-light': '#f5a0a0',
        success: '#12aa9c',        // 青矾绿 - 成功
        'success-light': '#b7e8e6',

        // Apple 基础灰阶
        'sys-bg': 'transparent',       // 页面背景 (透明以显示全局背景)
        'sys-bg-secondary': '#F2F0EB', // 次级背景
        'sys-bg-warm': '#F7F3EC',  // 暖调背景
        'sys-card': 'rgba(255, 255, 255, 0.80)', // 磨砂卡片
        'sys-card-solid': '#FFFFFF',
        'sys-divider': 'rgba(0, 0, 0, 0.06)',
        'sys-overlay': 'rgba(255, 255, 255, 0.72)',

        // 文字层级
        'text-primary': '#1D1D1F', // Apple 黑 - 主要标题
        'text-secondary': '#6E6E73', // Apple 灰 - 正文
        'text-tertiary': '#AEAEB2', // 浅灰 - 辅助

        // 保留国风色 (降低饱和度融入 Apple 体系)
        ink: '#1D1D1F',
        'ink-light': '#6E6E73',
        gold: '#c8851a',
        'gold-light': '#f5d68a',
        vermilion: '#e54d42',
        cyan: '#12aa9c',
        'cyan-light': '#b7e8e6',
        moon: '#E8F0F2',
        bamboo: '#5b6e4b',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', '"SF Pro Display"', '"SF Pro Text"', '"PingFang SC"', '"Microsoft YaHei"', 'sans-serif'],
        kai: ['"Noto Serif SC"', '"KaiTi"', '"楷体"', '"STKaiti"', 'serif'],
        song: ['"SimSun"', '"宋体"', '"STSong"', 'serif'],
      },
      borderRadius: {
        'apple': '12px',
        'apple-lg': '16px',
        'apple-xl': '20px',
      },
      boxShadow: {
        'apple-sm': '0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04)',
        'apple': '0 2px 6px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05)',
        'apple-lg': '0 4px 12px rgba(0,0,0,0.10), 0 2px 4px rgba(0,0,0,0.06)',
        'apple-xl': '0 8px 24px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.06)',
        'inset-sm': 'inset 0 1px 2px rgba(0,0,0,0.04)',
        'inset': 'inset 0 2px 4px rgba(0,0,0,0.06)',
        'inset-lg': 'inset 0 3px 6px rgba(0,0,0,0.08)',
        'zen-card': '0 2px 6px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.05), inset 0 1px 2px rgba(0,0,0,0.04), inset 0 0 0 1px rgba(255,255,255,0.5)',
      },
      borderColor: {
        'zen': 'rgba(200, 133, 26, 0.12)',
        'zen-strong': 'rgba(200, 133, 26, 0.18)',
        'zen-light': 'rgba(200, 133, 26, 0.06)',
      },
      letterSpacing: {
        'zen-wide': '0.15em',
      },
      backdropBlur: {
        'apple': '20px',
        'apple-lg': '40px',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-in-out',
        'slide-up': 'slideUp 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'scale-in': 'scaleIn 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' }
        }
      }
    }
  },
  plugins: []
}
