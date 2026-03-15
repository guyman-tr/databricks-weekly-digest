import nodemailer from "nodemailer";

function getTransporter() {
  return nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.SMTP_USER,
      pass: process.env.SMTP_PASS,
    },
  });
}

function getBaseUrl(): string {
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    return process.env.NEXT_PUBLIC_SITE_URL;
  }
  if (process.env.VERCEL_PROJECT_PRODUCTION_URL) {
    return `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}`;
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "https://databricks-weekly-digest-guyman-2003s-projects.vercel.app";
}

export async function sendConfirmationEmail(
  email: string,
  token: string
): Promise<void> {
  const baseUrl = getBaseUrl();
  const confirmUrl = `${baseUrl}/api/confirm?token=${token}`;

  const transporter = getTransporter();
  await transporter.sendMail({
    from: `"Databricks Weekly" <${process.env.SMTP_USER}>`,
    to: email,
    subject: "Confirm your Databricks Weekly subscription",
    text: [
      "Thanks for subscribing to Databricks Weekly!",
      "",
      "Click the link below to confirm your subscription:",
      confirmUrl,
      "",
      "If you didn't sign up, you can safely ignore this email.",
    ].join("\n"),
    html: `
      <div style="font-family: -apple-system, system-ui, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px;">
        <h2 style="color: #FF3621; margin: 0 0 16px;">Databricks Weekly</h2>
        <p style="color: #333; line-height: 1.6;">Thanks for subscribing! Click the button below to confirm your subscription.</p>
        <a href="${confirmUrl}" style="display: inline-block; margin: 24px 0; padding: 12px 28px; background: #FF3621; color: white; text-decoration: none; border-radius: 8px; font-weight: 600;">Confirm Subscription</a>
        <p style="color: #888; font-size: 13px; line-height: 1.5;">If you didn't sign up, you can safely ignore this email.</p>
      </div>
    `,
  });
}
