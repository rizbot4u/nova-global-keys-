import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Navbar from '@/components/Navbar'
import FooterSection from '@/components/FooterSection'
import { AuthProvider } from '@/contexts/AuthContext' // Added this
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Trading Bots - Automate Your Trading',
  description: 'Powerful AI trading bots for crypto and forex markets.',
  icons: {
    icon: '/favicon.ico',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        {/* Wrap everything in AuthProvider */}
        <AuthProvider>
          <Navbar />
          <main>{children}</main>
          <FooterSection />
        </AuthProvider>
      </body>
    </html>
  )
}
