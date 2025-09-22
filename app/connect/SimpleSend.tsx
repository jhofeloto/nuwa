import { useState } from "react";
import { useWallet } from "./useWallet";
import { Lucid } from "@/app/lib/lucid-client";
import { Card, Flex, Text, Box, TextField } from "@radix-ui/themes";
import { Button } from "@/app/ui/button";

interface SimpleSendProps {
  lovelaceAmount?: string;
  lucidInstance: Awaited<ReturnType<typeof Lucid>> | null;
}

const SimpleSend = ({ lucidInstance }: SimpleSendProps) => {
  const { usedAddresses } = useWallet();
  const [isLoading, setIsLoading] = useState(false);
  const [txHash, setTxHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [toAddress, setToAddress] = useState<string>("");
  const [amount, setAmount] = useState<string>("");

  const handleSendAda = async () => {
    if (!usedAddresses?.[0]) {
      setError("Please connect your wallet first");
      return;
    }

    if (!lucidInstance) {
      setError("Lucid not initialized. Please connect your wallet first.");
      return;
    }

    if (!toAddress || !amount) {
      setError("Please provide a valid address and amount.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setTxHash(null);

    try {
      const lovelaceAmount = BigInt(Number(amount) * 1_000_000);
      const tx = await lucidInstance
        .newTx()
        .pay.ToAddress(usedAddresses[0], { lovelace: lovelaceAmount} )
        .complete();

      const signedTx = await tx.sign.withWallet().complete();
      const txHash = await signedTx.submit();

      setTxHash(txHash);
      console.log("Transaction submitted successfully!", txHash);
    } catch (err) {
      if (err instanceof Error && err.message.includes("user declined sign tx")) {
        setError("Transaction signing was canceled by the user.");
      } else {
        console.error("Transaction failed:", err);
        setError(err instanceof Error ? err.message : "Transaction failed");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card size="4">
      <Flex direction="column" gap="4">
        <Text size="1" color="mint">
          To Address:
        </Text>
        <TextField.Root
          placeholder="Insert address here..."
          value={toAddress}
          onChange={(e) => setToAddress(e.target.value)}
        />
        <Text size="1" color="mint">
          Amount:
        </Text>
        <TextField.Root
          type="number"
          placeholder="₳ 0.000000"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <Button
          onClick={handleSendAda}
          disabled={isLoading}
          variant="outline"
          className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
        >
          {isLoading ? "Sending..." : "Send ADA"}
        </Button>

        {txHash && (
          <Box>
            <Text size="3" color="mint">
              Transaction submitted!
            </Text>
            <a
              href={`https://preprod.cardanoscan.io/transaction/${txHash}`}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "blue", textDecoration: "none" }}
            >
              View on Explorer
            </a>
          </Box>
        )}

        {error && (
          <Text size="3" color="tomato">
            Error: {error}
          </Text>
        )}
      </Flex>
    </Card>
  );
};

export default SimpleSend;