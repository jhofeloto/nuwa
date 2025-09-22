import { useEffect, useState, useCallback } from "react";
import { getLucidWasmBindings, Lucid, MintingPolicy } from "@/app/lib/lucid-client";
import { applyParams, readValidators } from "../lib/utils";
import { AppliedValidators } from "@/app/lib/definitions";
import CopyButton from "./copyButton";
import { Card, Flex, Text, Box, TextField, Tabs } from "@radix-ui/themes";
import { Button } from "@/app/ui/button";
import { Spinner } from "@radix-ui/themes";
import { storeContractData, getContractByPolicyId, updateContractData } from "../actions/contracts";
import { Contracts } from "@prisma/client";

interface LockGiftCardProps {
  instance: Awaited<ReturnType<typeof Lucid>>;
  usedAddresses: string[];
  isActive?: boolean;
}

// Interface for wallet assets
interface AssetInfo {
  policyId: string;
  assetName: string;
  amount: string;
}

const tokenName = "NuwaGiftCard";

const LockGiftCard: React.FC<LockGiftCardProps> = ({ instance, usedAddresses, isActive = false }) => {
  console.log("LockGiftCard rendered - isActive:", isActive);
  const [validator, setValidator] = useState<string>("");
  const [destinAddress, setDestinAddress] = useState<string>("");
  const [walletAddress, setWalletAddress] = useState<string>("");
  const [lucidInstance, setLucidInstance] = useState<Awaited<
    ReturnType<typeof Lucid>
  > | null>(null);
  const [contracts, setContracts] = useState<AppliedValidators>(() => ({} as AppliedValidators));
  const [amount, setAmount] = useState<string>("");
  const [watingLockTx, setWatingLockTx] = useState<boolean>(false);
  const [lockTxHash, setLockTxHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validatorsLoaded, setValidatorsLoaded] = useState(false);
  const [checkingAssets, setCheckingAssets] = useState(false);
  const [walletAssets, setWalletAssets] = useState<AssetInfo[]>([]);
  const [giftCardFound, setGiftCardFound] = useState(false);
  const [giftCardChecked, setGiftCardChecked] = useState(false);
  const [foundContracts, setFoundContracts] = useState<Contracts[]>([]);
  const [activeTab, setActiveTab] = useState("check");

  const checkGiftCard = useCallback(async () => {
    if (!lucidInstance || !walletAddress) {
      console.error("Cannot check gift card: Missing lucidInstance or walletAddress");
      setError("Cannot check gift card: Wallet not connected");
      return;
    }
    
    setCheckingAssets(true);
    setGiftCardChecked(false);
    setError(null);
    setFoundContracts([]);
    
    try {
      const lucid = await getLucidWasmBindings();
      console.log("Checking gift cards in wallet:", walletAddress);
      const utxos = await lucidInstance.utxosAt(walletAddress);
      console.log("UTXOs found:", utxos.length);
      
      if (utxos.length === 0) {
        console.error("No UTXOs found in wallet");
        setWalletAssets([]);
        setGiftCardFound(false);
        setGiftCardChecked(true);
        setCheckingAssets(false);
        return;
      }
      
      const allAssets: AssetInfo[] = [];
      let foundGiftCard = false;
      const foundContractsArray: Contracts[] = [];
      
      for (const utxo of utxos) {
        console.log("UTXO:", utxo.txHash, "assets:", utxo.assets);
        
        if (utxo.assets) {
          for (const [unit, quantity] of Object.entries(utxo.assets)) {
            if (unit === "lovelace") continue;
            
            const policyId = unit.slice(0, 56);
            const assetNameHex = unit.slice(56);
            let assetName = "";
            assetName = new TextDecoder().decode(lucid.fromHex(assetNameHex));
              
            console.log("Asset found:", assetName, "Policy ID:", policyId);
              
            // Add asset to the list
            allAssets.push({
              policyId,
              assetName,
              amount: quantity.toString()
            });
              
            // Try to find contract in the database
            try {
              const contractInfo = await getContractByPolicyId(policyId);
              
              if (contractInfo) {
                console.log("Found contract in database:", contractInfo);
                foundContractsArray.push(contractInfo as Contracts);
                
                // Check if this is a gift card based on contract details
                if (
                  contractInfo.contractName === "GiftCard" || 
                  (contractInfo.tokenName && 
                    (contractInfo.tokenName === "NuwaGiftCard"))
                ) {
                  console.log("Gift card contract found in database!");
                  foundGiftCard = true;
                  const giftCard: MintingPolicy = contractInfo.compiledCode as unknown as MintingPolicy;
                  const contractDB: AppliedValidators = {
                    policyId: contractInfo.contractId,
                    lockAddress: contractInfo.contractAddress || "",
                    giftCard: giftCard,
                    redeem: giftCard,
                  };
                  setContracts(contractDB);
                }
              }
            } catch (err) {
              console.error("Error fetching contract for policy ID", policyId, ":", err);
            }
            
            // Also check if this might be our gift card based on asset name
            if (!foundGiftCard && (assetName === "NuwaGiftCard")) {
              foundGiftCard = true;
            }
          }
        }
      }
        
      console.log("All assets found:", allAssets);
      setWalletAssets(allAssets);
      setFoundContracts(foundContractsArray);
      setGiftCardFound(foundGiftCard);
      
      if (allAssets.length === 0) {
        console.log("No assets found in wallet (besides ADA)");
      }
    } catch (err) {
      console.error("Error checking gift card:", err);
      setError(err instanceof Error ? err.message : "Failed to check wallet assets");
    } finally {
      setCheckingAssets(false);
      setGiftCardChecked(true);
    }
  }, [lucidInstance, walletAddress]);

  const loadValidators = useCallback(() => {
    try {
      console.log("Loading validators...");
      
      if (typeof readValidators !== 'function') {
        console.error("readValidators is not a function", typeof readValidators);
        setError("readValidators function is not available");
        return;
      }
      
      console.log("Calling readValidators()");
      const validators = readValidators();
      console.log("Validators loaded:", validators);
      
      if (validators && validators.giftCard) {
        setValidator(validators.giftCard);
        setValidatorsLoaded(true);
        setError(null);
        console.log("Validator successfully set");
      } else {
        console.error("Invalid validator structure returned:", validators);
        setError("Failed to load validators: Invalid structure");
      }
    } catch (err) {
      console.error("Error loading validators:", err);
      setError(err instanceof Error ? err.message : "Failed to load validators");
    }
  }, []);

  useEffect(() => {
    if (instance) {
      setLucidInstance(instance);
    }
  }, [instance]);

  useEffect(() => {
    if (usedAddresses?.[0] && usedAddresses[0] !== walletAddress) {
      setWalletAddress(usedAddresses[0]);
    }
  }, [usedAddresses, walletAddress]);
  
  useEffect(() => {
    console.log("isActive changed:", isActive, "validatorsLoaded:", validatorsLoaded);
    if (isActive && !validatorsLoaded) {
      console.log("Loading validators because tab is active");
      loadValidators();
    }
  }, [isActive, validatorsLoaded, loadValidators]);
  
  useEffect(() => {
    if (isActive && lucidInstance && walletAddress) {
      console.log("Checking gift card because tab is active and we have lucidInstance and walletAddress");
      checkGiftCard();
    }
  }, [isActive, lucidInstance, walletAddress, checkGiftCard]);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!validatorsLoaded) {
        console.log("Fallback: Loading validators on component mount");
        loadValidators();
      }
    }, 1000);
    
    return () => clearTimeout(timer);
  }, [validatorsLoaded, loadValidators]);

  async function createContract() {
    setIsLoading(true);
    try {
      if (walletAddress) {
        const utxos = await lucidInstance!.utxosAt(walletAddress);
        const utxo = utxos[0];
        if (!utxo) {
          console.error("No UTXOs found");
          return;
        }
        const outputReferente = {
          txHash: utxo.txHash,
          outputIndex: utxo.outputIndex,
        };
        console.log("utxo", utxo);
        console.log("walletAddress", walletAddress);

        
        console.log("validator", validator);
        console.log("outputReferente", outputReferente);
        console.log("tokenName", tokenName);

        const newContracts = await applyParams(tokenName, outputReferente, validator);
        console.log("contracts", newContracts);
        setContracts(newContracts);
      } else {
        console.error("Wallet address is null");
      }
    } catch (err) {
      console.error("Error creating contract:", err);
      setError(err instanceof Error ? err.message : "Failed to create contract");
    } finally {
      setIsLoading(false);
    }
  }

  async function createGiftCard(destinAddress: string, amount: string) {
    const lucid = await getLucidWasmBindings();

    setWatingLockTx(true);
    setLockTxHash(null);
    setError(null);

    try {
      const parsedAmount = parseFloat(amount);

      if (isNaN(parsedAmount) || parsedAmount <= 0) {
        throw new Error("Invalid amount. Please enter a positive number.");
      }

      const lovelaceAmount = BigInt(Math.floor(parsedAmount * 1_000_000));

      const assetName = `${contracts.policyId}${lucid.fromText(tokenName)}`;

      const mintRedeemer = lucid.Data.to(new lucid.Constr(0, []));
      const utxos = await lucidInstance!.utxosAt(walletAddress);
      const utxo = utxos[0];

      if (!utxo) {
        throw new Error("No UTXOs found for the wallet address.");
      }

      const tx = await lucidInstance!
        .newTx()
        .collectFrom([utxo])
        .attach.MintingPolicy(contracts!.giftCard)
        .mintAssets({ [assetName]: 1n }, mintRedeemer)
        .pay.ToContract(
          contracts.lockAddress,
          { kind: "inline", value: lucid.Data.void() },
          { lovelace: lovelaceAmount }
        )
        .pay.ToAddress(destinAddress, {[assetName]: 1n})
        .complete();

      const signedTx = await tx.sign.withWallet().complete();
      console.log("Signed transaction:", signedTx);

      const txHash = await signedTx.submit();
      console.log("Transaction hash:", txHash);

      const success = await lucidInstance!.awaitTx(txHash);

      console.log("Transaction success:", success);

      setTimeout(async () => {
        setWatingLockTx(false);

        if (success) {
          console.log("Transaction submitted successfully!", txHash);
          const contractName = "GiftCard";
          const contractType = "Mint | Spending";
          console.log("Storing contract data...", contractName, contractType, tokenName, contracts, txHash);
          try {
            await storeContractData(
              contractName,
              contractType,
              tokenName,
              contracts,
              txHash,
              walletAddress,
              lovelaceAmount,
              { [assetName]: 1n }
            );
            setLockTxHash(txHash);
            
            setTimeout(() => checkGiftCard(), 2000);
          } catch (err) {
            console.error("Error storing contract data:", err);
            setError(err instanceof Error ? err.message : "Failed to store contract data");
          }
        }
      }, 3000);
    } catch (err) {
      if (
        err instanceof Error &&
        err.message.includes("user declined sign tx")
      ) {
        console.warn("Transaction signing was canceled by the user.");
        setError("Transaction signing was canceled by the user.");
      } else {
        console.error("Error creating gift card:", err);
        setError(err instanceof Error ? err.message : "Transaction failed");
      }
    } finally {
      setWatingLockTx(false);
    }
  }

  async function redeemGiftCard() {
    const lucid = await getLucidWasmBindings();

    setWatingLockTx(true);
    setLockTxHash(null);
    setError(null);

    try {
      // Log the contract we're using for redemption
      console.log("Redeeming gift card using contract:", contracts);
      
      if (!contracts.policyId || !contracts.giftCard || !contracts.redeem || !contracts.lockAddress) {
        throw new Error("Incomplete contract information. Please check wallet for gift card token first.");
      }

      const assetName = `${contracts.policyId}${lucid.fromText(tokenName)}`;
      const burnRedeemer = lucid.Data.to(new lucid.Constr(1, []));
      
      const utxos = await lucidInstance!.utxosAt(contracts.lockAddress);
      
      if (!utxos || utxos.length === 0) {
        throw new Error("No UTXOs found at contract address: " + contracts.lockAddress);
      }
      
      const utxo = utxos[0];
      console.log("Using UTXO for redemption:", utxo);
      
      const tx = await lucidInstance!
        .newTx()
        .collectFrom([utxo], lucid.Data.void())
        .attach.MintingPolicy(contracts.giftCard)
        .attach.SpendingValidator(contracts.giftCard)
        .mintAssets({ [assetName]: -1n }, burnRedeemer)
        .complete();

      const signedTx = await tx.sign.withWallet().complete();
      console.log("Signed transaction:", signedTx);
      
      const txHash = await signedTx.submit();
      console.log("Transaction submitted with hash:", txHash);

      const success = await lucidInstance!.awaitTx(txHash);
      console.log("Transaction success:", success);

      // Changed to use async arrow function
      setTimeout(async () => {
        setWatingLockTx(false);

        if (success) {
          try {
            await updateContractData(contracts.policyId);
            console.log("Gift card successfully redeemed!");
            setLockTxHash(txHash);
            setTimeout(() => checkGiftCard(), 2000);
          } catch (err) {
            console.error("Error updating contract data:", err);
            setError(err instanceof Error ? err.message : "Failed to update contract data");
          }
        }
      }, 3000);
    } catch (err) {
      if (
        err instanceof Error &&
        err.message.includes("Your wallet does not have enough funds")
      ) {
        console.warn("Insufficient funds in the wallet.");
        setError("Your wallet does not contain a gift card to redeem.");
      } else if (
        err instanceof Error &&
        err.message.includes("UTxOs with reference scripts")
      ) {
        console.warn("UTxOs with reference scripts are excluded from coin selection."); 
        setError("Your wallet contains UTxOs with reference scripts, which are excluded from coin selection.");
      } else if (
        err instanceof Error &&
        err.message.includes("user declined sign tx")
      ) {
        console.warn("Transaction signing was canceled by the user."); 
        setError("Transaction signing was canceled by the user.");
      } else {
        console.error("Error redeeming gift card:", err);
        setError(err instanceof Error ? err.message : "Transaction failed: " + (err instanceof Error ? err.message : String(err)));
      }
    } finally {
      setWatingLockTx(false);
    }
  }
    
  return (
    <Card size="4">
      <Tabs.Root defaultValue="check" onValueChange={setActiveTab}>
        <Tabs.List>
          <Tabs.Trigger value="check">Check Gift Cards</Tabs.Trigger>
          <Tabs.Trigger value="create">Create Gift Card</Tabs.Trigger>
        </Tabs.List>
        
        {/* Check Gift Cards Tab */}
        <Tabs.Content value="check">
          <Flex justify="between" gap="4" direction="column" style={{ width: "100%", padding: "1rem" }}>
            <Box style={{ width: "100%" }}>
              <Flex align="center" justify="between" style={{ width: "100%" }}>
                <Button
                  onClick={() => checkGiftCard()}
                  disabled={!lucidInstance || !walletAddress || checkingAssets}
                  variant="outline"
                  className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
                >
                  {checkingAssets ? <Spinner /> : "Check for Gift Cards"}
                </Button>
              </Flex>
              
              {/* Display found contracts from database */}
              {foundContracts.length > 0 && (
                <Box style={{ marginTop: "0.5rem" }}>
                  <Text size="2" color="mint">
                    Found {foundContracts.length} contract{foundContracts.length !== 1 ? "s" : ""} in database:
                  </Text>
                  <Box 
                    style={{ 
                      border: "1px solid var(--mint-6)", 
                      borderRadius: "0.25rem", 
                      padding: "0.5rem",
                      marginTop: "0.25rem",
                      maxHeight: "150px",
                      overflowY: "auto"
                    }}
                  >
                    {foundContracts.map((contract, index) => (
                      <Text key={index} size="2" style={{ marginBottom: "0.25rem" }}>
                        • {contract.contractName} ({contract.contractType}) 
                        <Text size="1" style={{ display: "block", color: "var(--gray-11)" }}>
                          ID: {contract.contractId.slice(0, 8)}...{contract.contractId.slice(-8)}
                          {contract.tokenName ? ` | Token: ${contract.tokenName}` : ''}
                        </Text>
                      </Text>
                    ))}
                  </Box>
                </Box>
              )}
              
              {walletAddress && walletAssets.length > 0 && (
                <Box style={{ marginTop: "0.5rem" }}>
                  <Text size="2" color="mint">
                    Found {walletAssets.length} token{walletAssets.length !== 1 ? "s" : ""} in wallet:
                  </Text>
                  <Box 
                    style={{ 
                      border: "1px solid var(--mint-6)", 
                      borderRadius: "0.25rem", 
                      padding: "0.5rem",
                      marginTop: "0.25rem",
                      maxHeight: "150px",
                      overflowY: "auto"
                    }}
                  >
                    {walletAssets.map((asset, index) => (
                      <Text key={index} size="2" style={{ marginBottom: "0.25rem" }}>
                        • {asset.assetName} ({asset.amount}) 
                        <Text size="1" style={{ display: "block", color: "var(--gray-11)" }}>
                          Policy: {asset.policyId.slice(0, 8)}...{asset.policyId.slice(-8)}
                        </Text>
                      </Text>
                    ))}
                  </Box>
                  {giftCardFound && (
                    <Text size="2" color="mint" style={{ fontWeight: "bold", marginTop: "0.25rem" }}>
                      Gift Card detected in wallet!
                    </Text>
                  )}
                </Box>
              )}
              
              {walletAddress && !giftCardFound && giftCardChecked && !checkingAssets && (
                <Text size="2" color="tomato" style={{ marginTop: "0.5rem" }}>
                  Connected address does not contain a gift card.
                </Text>
              )}
            </Box>
            
            <Button
              onClick={() => redeemGiftCard()}
              disabled={!contracts.policyId || watingLockTx || (!giftCardFound && giftCardChecked)}
              variant="outline"
              className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
            >
              {watingLockTx ? <Spinner /> : "Claim Gift"}
            </Button>
            
            {lockTxHash && activeTab === "check" && (
              <Flex align="center" justify="between" gap="4">
                <Text size="3" color="mint">
                  Transaction submitted!
                </Text>
                <Box style={{ flex: 1 }}>
                  <Flex align="center" gap="2">
                    <TextField.Root
                      readOnly
                      value={lockTxHash}
                      style={{ width: "100%" }}
                    />
                    <CopyButton text={lockTxHash} />
                  </Flex>
                </Box>
                <Box>
                  <Button
                    href={`https://preview.cardanoscan.io/transaction/${lockTxHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
                    style={{
                      textDecoration: "none",
                      textAlign: "center",
                      display: "inline-block",
                      padding: "8px 16px",
                      borderRadius: "4px",
                    }}
                  >
                    View on Explorer
                  </Button>
                </Box>
              </Flex>
            )}
            
            {error && activeTab === "check" && (
              <Text size="3" color="tomato">
                Error: {error}
              </Text>
            )}
          </Flex>
        </Tabs.Content>
        
        {/* Create Gift Card Tab */}
        <Tabs.Content value="create">
          <Flex justify="between" gap="4" direction="column" style={{ width: "100%", padding: "1rem" }}>
            <Text size="4" color="mint">
              Create a Gift Card
            </Text>
            <Text size="1" color="mint">
              This contract allows you to mint a token as a gift card to lock ADA in the smart contract. The locked ADA can only be redeemed by the wallet in possession of the gift card and after burning it.
            </Text>
            
            {/* Validator Section */}
            <Box style={{ flex: 1, width: "100%" }}>
              <Text size="3" color="mint">
                Validator:
              </Text>
              <Flex align="center" gap="2" style={{ width: "100%" }}>
                <TextField.Root
                  readOnly
                  value={validator ? `${validator.slice(0, 20)}...${validator.slice(-20)}` : "Validator not loaded"}
                  style={{ width: "100%" }}
                />
                {validator && <CopyButton text={validator} />}
                {!validator && (
                  <Button 
                    onClick={() => loadValidators()} 
                    variant="outline" 
                    className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
                  >
                    Load Validator
                  </Button>
                )}
              </Flex>
            </Box>
            
            <Button
              onClick={() => createContract()}
              disabled={isLoading || watingLockTx || !validator || !walletAddress}
              variant="outline"
              className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
            >
              {isLoading ? <Spinner /> : "Make Contract"}
            </Button>

            {contracts && contracts.redeem && contracts.redeem.script && (
              <Box>
                <Text size="1" color="mint">
                  Compiled Contract:
                </Text>
                <Flex align="center" gap="2">
                  <TextField.Root
                    readOnly
                    value={`${contracts.redeem.script.slice(0, 20)}...${contracts.redeem.script.slice(-20)}`}
                  />
                  <CopyButton text={contracts.redeem.script} />
                </Flex>
                <Text size="1" color="mint">
                  Contract Lock Address:
                </Text>
                <TextField.Root readOnly value={contracts.lockAddress} />
                <Text size="1" color="mint">
                  ADA Amount:
                </Text>
                <TextField.Root
                  type="number"
                  placeholder="₳ 0.000000"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  style={{ width: "100%" }}
                />
                <Text size="1" color="mint">
                  Beneficiary Address:
                </Text>
                <TextField.Root
                  placeholder="Enter addr_test1..."
                  value={destinAddress}
                  onChange={(e) => setDestinAddress(e.target.value)}
                  style={{ width: "100%" }}
                />
                <Flex gap="2" p="2">
                  <Button
                    onClick={() => createGiftCard(destinAddress, amount)}
                    disabled={!contracts || !amount.trim() || !destinAddress.trim() || watingLockTx || lockTxHash !== null}
                    variant="outline"
                    className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
                  >
                    {watingLockTx ? <Spinner /> : "Create Transaction"}
                  </Button>
                </Flex>
              </Box>
            )}

            {lockTxHash && activeTab === "create" && (
              <Flex align="center" justify="between" gap="4">
                <Text size="3" color="mint">
                  Transaction submitted!
                </Text>
                <Box style={{ flex: 1 }}>
                  <Flex align="center" gap="2">
                    <TextField.Root
                      readOnly
                      value={lockTxHash}
                      style={{ width: "100%" }}
                    />
                    <CopyButton text={lockTxHash} />
                  </Flex>
                </Box>
                <Box>
                  <Button
                    href={`https://preview.cardanoscan.io/transaction/${lockTxHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-white dark:bg-zinc-800 border-mint-6 dark:border-mint-8 text-mint-11 dark:text-mint-9 hover:bg-mint-3 dark:hover:bg-zinc-700 transition-colors"
                    style={{
                      textDecoration: "none",
                      textAlign: "center",
                      display: "inline-block",
                      padding: "8px 16px",
                      borderRadius: "4px",
                    }}
                  >
                    View on Explorer
                  </Button>
                </Box>
              </Flex>
            )}

            {error && activeTab === "create" && (
              <Text size="3" color="tomato">
                Error: {error}
              </Text>
            )}
          </Flex>
        </Tabs.Content>
      </Tabs.Root>
    </Card>
  );
};

export default LockGiftCard;