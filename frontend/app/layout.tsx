import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StudyX AI",
  description: "Your focused AI study companion",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
