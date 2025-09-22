import { useState } from "react";
import { theme } from "../app.config";

export default function CopyButton({ text }: { text: string }) { // Ensure text is explicitly typed as a string
  const [showCopied, setShowCopied] = useState(false);

  const handleCopy = async (text: string, setShowCopied: React.Dispatch<React.SetStateAction<boolean>>) => {
    if (typeof window !== "undefined" && text.trim()) { // Ensure text is not empty or whitespace
      await navigator.clipboard.writeText(text);
      setShowCopied(true);
      setTimeout(() => setShowCopied(false), 2000);
    } else {
      console.error("Cannot copy: text is empty or invalid");
    }
  };

  return (
    <button
      onClick={() => handleCopy(text, setShowCopied)}
      style={{
        background: theme.colors.background.secondary,
        border: `1px solid ${theme.colors.border.secondary}`,
        borderRadius: "6px",
        width: "32px",
        height: "32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        cursor: "pointer",
        color: showCopied
          ? theme.colors.primary
          : theme.colors.text.secondary,
        fontSize: "0.75rem",
        transition: "all 0.2s ease",
        position: "relative",
      }}
      title="Copy address"
    >
      {showCopied ? "✓" : "⎘"}
    </button>
  );
}