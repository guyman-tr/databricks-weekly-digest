import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import SubscribeForm from "@/components/SubscribeForm";

export const metadata: Metadata = {
  title: "Databricks Weekly",
  description: "Weekly digest and podcast covering the latest Databricks developments",
  icons: {
    icon: "/favicon.png",
    apple: "/favicon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased min-h-screen">
        <Header />
        <main>{children}</main>
        <section className="max-w-3xl mx-auto px-6 py-12">
          <SubscribeForm />
        </section>
        <footer className="border-t border-white/5 mt-8">
          <div className="max-w-5xl mx-auto px-6 py-8 text-center text-xs text-brand-muted">
            Built with Gemini TTS & a weekly cron job.
            Content aggregated from Databricks blog, YouTube, and release notes.
          </div>
        </footer>
      </body>
    </html>
  );
}
