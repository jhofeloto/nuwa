"use client"

import * as React from "react"
import { MoonIcon, SunIcon } from "@radix-ui/react-icons"
import { useTheme } from "next-themes"
import { IconButton } from "@radix-ui/themes"

export default function ThemeToggle() {
  const { setTheme, theme } = useTheme()
  
  return (
    <IconButton
      variant="ghost"
      className="theme-toggle-button"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      {theme === "dark" ? (
        <MoonIcon className="h-4 w-4" />
      ) : (
        <SunIcon className="h-4 w-4" />
      )}
    </IconButton>
  )
}