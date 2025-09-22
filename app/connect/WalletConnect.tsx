import { useWallet } from "./useWallet";
import { useState, useEffect } from "react";
import ConnectButton from "./ConnectButton";
import CopyButton from "./copyButton";
import { Card, Flex, Text, Badge } from "@radix-ui/themes";

const WalletConnect = () => {
  const { isConnected, stakeAddress, accountBalance, usedAddresses } = useWallet();
  const [walletAddress, setWalletAddress] = useState<string | null>(null);

  useEffect(() => {
    if (usedAddresses?.[0] && usedAddresses[0] !== walletAddress) {
      setWalletAddress(usedAddresses[0]);
    }
  }, [usedAddresses, walletAddress]);

  if (!isConnected) {
    return (
      <Card size="4" style={{ textAlign: "center", padding: "4rem" }}>
        <ConnectButton />
      </Card>
    );
  }

  return (
    <Card size="4">
      <Flex direction="column" gap="4">
        <Flex align="center" justify="between">
          <Text size="3" color="gray">
            Stake Address
          </Text>
          <Flex align="center" gap="2">
            <Badge color="gray" radius="full">
              {stakeAddress
                ? `${stakeAddress.slice(0, 10)}...${stakeAddress.slice(-6)}`
                : "Not available"}
            </Badge>
            {stakeAddress && <CopyButton text={stakeAddress} />}
          </Flex>
        </Flex>

        <Flex align="center" justify="between">
          <Text size="3" color="gray">
            Account Address
          </Text>
          <Flex align="center" gap="2">
            <Badge color="gray" radius="full">
              {walletAddress
                ? `${walletAddress.slice(0, 10)}...${walletAddress.slice(-6)}`
                : "Not available"}
            </Badge>
            {walletAddress && <CopyButton text={walletAddress} />}
          </Flex>
        </Flex>

        <Flex align="center" justify="between">
          <Text size="3" color="gray">
            Balance
          </Text>
          <Flex align="baseline" gap="1">
            <Text size="5" weight="bold" color="mint">
              {accountBalance || "0"}
            </Text>
            <Text size="3" color="gray">
              ₳
            </Text>
          </Flex>
        </Flex>
      </Flex>
    </Card>
  );
};

export default WalletConnect;