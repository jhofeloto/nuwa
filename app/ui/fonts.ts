import { Inter, Lusitana, Roboto } from "next/font/google";

export const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const lusitana = Lusitana({ weight: ['400', '700'], subsets: ["latin"] });

export const roboto = Roboto({ weight: ['400'], subsets: ["latin"] });