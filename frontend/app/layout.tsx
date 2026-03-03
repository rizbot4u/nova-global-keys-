import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Navbar from '@/components/Navbar'
import FooterSection from '@/components/FooterSection'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Trading Bots - Automate Your Trading',
  description: 'Powerful AI trading bots for crypto and forex markets. Automate your trading strategies with our advanced algorithms.',
  icons: {
    icon: '/favicon.ico', // Default favicon
    shortcut: '/favicon-16x16.png', // For shortcuts
    apple: '/apple-touch-icon.png', // For Apple devices
  },
  // Alternative way to specify favicon
  // icons: [
  //   { rel: 'icon', url: '/favicon.ico' },
  //   { rel: 'icon', url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
  //   { rel: 'icon', url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
  //   { rel: 'apple-touch-icon', url: '/apple-touch-icon.png', sizes: '180x180' },
  // ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navbar />
        <main>{children}</main>
        <FooterSection />
      </body>
    </html>
  )
}