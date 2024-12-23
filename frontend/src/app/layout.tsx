import type { Metadata } from "next";
import Navigation from "@/components/Navigation";

import { Nunito } from 'next/font/google'

import "./globals.css";

const customFont = Nunito({ weight: "400", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Money",
  description: "AI Money",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${customFont.className} antialiased`}
      >

        <Navigation />
        {children}
      </body>
    </html>
  );
}
