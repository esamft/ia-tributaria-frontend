import type { Metadata } from "next";
import { Geist, Geist_Mono, Playfair_Display, Crimson_Text } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const playfairDisplay = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  display: 'swap',
});

const crimsonText = Crimson_Text({
  variable: "--font-crimson",
  subsets: ["latin"],
  weight: ['400', '600'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: "IA Tributária Internacional",
  description: "Especialista em tributação internacional com base RAG. Consulte sobre residência fiscal, tratados de bitributação e planejamento tributário.",
  keywords: "tributação internacional, residência fiscal, tratados fiscais, planejamento tributário, IA tributária",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${playfairDisplay.variable} ${crimsonText.variable} antialiased dark`}
      >
        {children}
      </body>
    </html>
  );
}
