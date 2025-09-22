'use client';
import WalletConnect from "./WalletConnect";
import SimpleSend from "./SimpleSend";
import "@/app/globals.css";
import { useEffect, useState, useRef, useCallback } from "react";
import { Lucid } from "@/app/lib/lucid-client";
import { useWallet } from "./useWallet";
import LockGiftCard from "./lockGiftCard";
import { lusitana } from "../ui/fonts";
import Breadcrumbs from "../ui/breadcrumbs";

export default function Page() {
  const { isConnected, usedAddresses, initLucid } = useWallet();
  const hasLoggedAddress = useRef(false);
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [lucidInstance, setLucidInstance] = useState<Awaited<
    ReturnType<typeof Lucid>
  > | null>(null);
  const [activeTab, setActiveTab] = useState<'SimpleSend' | 'GiftCard'>('SimpleSend');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const initialize = useCallback(async () => {
    try {
      if (!hasLoggedAddress.current) {
        const instance = await initLucid();
        if (instance) {
          setLucidInstance(instance);
          if (usedAddresses?.[0] && usedAddresses[0] !== walletAddress) {
            setWalletAddress(usedAddresses[0]);
            if (!hasLoggedAddress.current) {
              console.log("Connected wallet address:", usedAddresses[0]);
              hasLoggedAddress.current = true;
            }
          }
        }
      }
    } catch (error) {
      console.error("Error initializing Lucid:", error);
      setErrorMessage(
        "Failed to connect to the wallet. Please ensure your wallet is properly configured and an account is set."
      );
    }
  }, [initLucid, usedAddresses, walletAddress]);

  useEffect(() => {
    if (isConnected) {
      initialize();
    } else {
      setWalletAddress(null);
      setLucidInstance(null);
      hasLoggedAddress.current = false;
      setErrorMessage(null);
    }
  }, [initialize, isConnected]);

  return (
    <main className="min-h-screen">
      <div className="flex-grow md:overflow-y-auto md:p-12">
        <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl shadow-md p-6 mb-8 border border-mint-5 dark:border-mint-8">
          <Breadcrumbs
              breadcrumbs={[
                { label: 'Home', href: '/' },
                { label: 'Connect', href: '/connect', active: true }
              ]}
              />
          <h1 className={`${lusitana.className} mb-6 text-2xl md:text-3xl font-bold text-mint-11 dark:text-mint-9`}>
              Wallet Info
          </h1>
          <WalletConnect />
          {errorMessage && (
            <div className="text-red-500 mt-4">
              {errorMessage}
            </div>
          )}
        </div>
      
        {isConnected && walletAddress && (
            <div className="bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg rounded-xl shadow-md p-6 mb-8 border border-mint-5 dark:border-mint-8">
          <div className="mt-6">
                      <h2 className={`${lusitana.className} text-center px-2 mb-6 text-2xl md:text-3xl font-bold text-mint-11 dark:text-mint-9`}>
              Transactions
          </h2>
              <div className="container p-2 mx-auto py-2 flex border-b border-mint-6 dark:border-mint-8 mb-4">

                  <button
                    className={`px-4 py-2 text-sm font-medium transition-colors ${
                      activeTab === 'SimpleSend' 
                        ? 'border-b-2 border-mint-9 text-mint-11 dark:text-mint-9' 
                        : 'text-gray-500 hover:text-mint-11 dark:hover:text-mint-9'
                    }`}
                    onClick={() => setActiveTab('SimpleSend')}
                  >
                    {'Simple Send'}
                  </button>
                  <button
                    className={`px-4 py-2 text-sm font-medium transition-colors ${
                      activeTab === 'GiftCard' 
                        ? 'border-b-2 border-mint-9 text-mint-11 dark:text-mint-9' 
                        : 'text-gray-500 hover:text-mint-11 dark:hover:text-mint-9'
                    }`}
                    onClick={() => setActiveTab('GiftCard')}
                  >
                    {'GiftCard'}
                  </button>

              </div>
            
              {walletAddress && lucidInstance && activeTab === 'SimpleSend' && (
                <div>
                  <SimpleSend lucidInstance={lucidInstance} />
                </div>
              )}

              {walletAddress && lucidInstance && activeTab === 'GiftCard' && (
                <LockGiftCard instance={lucidInstance} usedAddresses={usedAddresses} />
              )}

            </div>
          </div>
        )}
      </div>
    </main>

  );
}
