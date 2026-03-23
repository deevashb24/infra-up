import type { Metadata } from 'next'
import { Inter, Noto_Sans_Devanagari } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const notoSansDeva = Noto_Sans_Devanagari({ 
    weight: ['400', '500', '600', '700'],
    subsets: ['devanagari'], 
    variable: '--font-noto-deva' 
})

export const metadata: Metadata = {
  title: 'UP Infra Intelligence',
  description: 'Live Project tracking & Alerts for Uttar Pradesh',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${notoSansDeva.variable} font-sans`}>{children}</body>
    </html>
  )
}
