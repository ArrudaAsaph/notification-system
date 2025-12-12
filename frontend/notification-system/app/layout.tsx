import type { Metadata, Viewport } from "next";
import Script from "next/script";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import ThemeToggle from "../components/ThemeToggle";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Notification System",
    template: "%s • Notification System",
  },
  description: "Frontend do sistema de notificações",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#0a0a0a" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <Script id="theme-initializer" strategy="beforeInteractive">
        {`
          try {
            const stored = localStorage.getItem('theme');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const isDark = stored ? stored === 'dark' : prefersDark;
            if (isDark) document.documentElement.classList.add('dark');
          } catch (_) {}
        `}
      </Script>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-zinc-50 text-zinc-900 dark:bg-black dark:text-zinc-50`}
      >
        <a href="#conteudo" className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50 focus:rounded-md focus:bg-zinc-100 focus:px-3 focus:py-2 focus:text-zinc-900 dark:focus:bg-zinc-800 dark:focus:text-zinc-50">Saltar para o conteúdo</a>
        <header className="sticky top-0 z-40 border-b border-zinc-200/70 bg-white/70 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:border-zinc-800/70 dark:bg-zinc-900/40 dark:supports-[backdrop-filter]:bg-zinc-900/30">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-6 w-6 rounded-md bg-zinc-900 dark:bg-zinc-100" aria-hidden="true" />
              <Link href="/" className="text-base font-semibold tracking-tight">
                Notification System
              </Link>
            </div>
            <nav className="flex items-center gap-4 text-sm text-zinc-600 dark:text-zinc-400">
              <Link href="/" className="hover:text-zinc-900 dark:hover:text-zinc-200">Home</Link>
              <ThemeToggle />
            </nav>
          </div>
        </header>

        <main id="conteudo" className="mx-auto max-w-6xl px-6 py-8 min-h-[calc(100vh-144px)]">
          {children}
        </main>

        <footer className="border-t border-zinc-200/70 bg-white/70 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:border-zinc-800/70 dark:bg-zinc-900/40 dark:supports-[backdrop-filter]:bg-zinc-900/30">
          <div className="mx-auto max-w-6xl px-6 py-6 text-sm text-zinc-600 dark:text-zinc-400">
            <p>© {new Date().getFullYear()} Notification System</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
