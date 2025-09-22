'use client';
import { useEffect, useState } from "react";
import { useWallet } from "./useWallet";
import { theme } from "./theme";
import { Button } from "@/app/ui/button";
// import type { Cardano } from "@lucid-evolution/core-types";
import type { Cardano } from "@/app/lib/lucid-client";


declare global {
  interface Window {
    cardano: Cardano;
  }
}

const ConnectButton = () => {
  const { isConnected, connect, disconnect, installedExtensions } = useWallet();

  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) return null;

  const handleConnect = () => {
    if (installedExtensions.length === 1) {
      connect(installedExtensions[0]);
    } else if (installedExtensions.length > 1) {
      const modal = document.getElementById(
        "wallet-modal",
      ) as HTMLDialogElement;
      if (modal) modal.showModal();
    }
  };

  return (
    <>
      <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
        <Button
          onClick={isConnected ? undefined : handleConnect}
          disabled={isConnected}
          variant="outline"
          className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
        >
          {isConnected ? "Connected" : "Click to connect your wallet"}
        </Button>
        {isConnected && (
          <Button
            onClick={disconnect}
            variant="outline"
            className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
            style={{
              width: "20px",
              height: "20px",
              padding: "0",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            ×
          </Button>
        )}
      </div>
      <dialog
        id="wallet-modal"
        style={{
          background: theme.colors.background.card,
          border: `1px solid ${theme.colors.border.primary}`,
          borderRadius: "12px",
          padding: "1.5rem",
          color: theme.colors.text.primary,
          maxWidth: "400px",
          width: "90%",
        }}
      >
        <div style={{ marginBottom: "1rem" }}>
          <h3
            style={{ margin: "0 0 1rem 0", color: theme.colors.text.primary }}
          >
            Select Wallet
          </h3>
          <div
            style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}
          >
            {installedExtensions.map((wallet: string) => (
              <button
                key={wallet}
                onClick={() => {
                  connect(wallet);
                  const modal = document.getElementById(
                    "wallet-modal",
                  ) as HTMLDialogElement;
                  if (modal) modal.close();
                }}
                style={{
                  background: theme.colors.background.secondary,
                  border: `1px solid ${theme.colors.border.secondary}`,
                  borderRadius: "8px",
                  padding: "0.75rem 1rem",
                  color: theme.colors.text.primary,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  transition: "all 0.2s ease",
                  width: "100%",
                }}
              >
                <span style={{ fontSize: "0.875rem" }}>{wallet}</span>
                {typeof window !== "undefined" && window.cardano[wallet]?.icon && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={window.cardano[wallet].icon}
                    alt={`${wallet} logo`}
                    style={{
                      width: "24px",
                      height: "24px",
                      objectFit: "contain",
                    }}
                  />
                )}
              </button>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            onClick={() => {
              const modal = document.getElementById(
                "wallet-modal",
              ) as HTMLDialogElement;
              if (modal) modal.close();
            }}
            style={{
              background: "transparent",
              border: "none",
              color: theme.colors.text.secondary,
              cursor: "pointer",
              padding: "0.5rem",
              fontSize: "0.875rem",
            }}
          >
            Close
          </button>
        </div>
      </dialog>
    </>
  );
};

export default ConnectButton;