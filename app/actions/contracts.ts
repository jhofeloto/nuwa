"use server";

import { AppliedValidators } from "@/app/lib/definitions";
import { prisma } from '@/prisma';
import { Assets } from "@lucid-evolution/lucid";
import { Prisma } from "@prisma/client";

// Define more specific types instead of using 'any'
type JsonValue = 
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [key: string]: JsonValue };

// Custom BigInt serializer to handle BigInt values in JSON
function serializeBigInt(obj: unknown): JsonValue {
  if (obj === null || obj === undefined) {
    return null;
  }
  
  if (typeof obj === 'bigint') {
    return obj.toString(); // Convert BigInt to string
  }
  
  if (Array.isArray(obj)) {
    return obj.map(serializeBigInt);
  }
  
  if (typeof obj === 'object' && obj !== null) {
    const result: Record<string, JsonValue> = {};
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        result[key] = serializeBigInt((obj as Record<string, unknown>)[key]);
      }
    }
    return result;
  }
  
  // For primitive types (string, number, boolean)
  if (typeof obj === 'string' || typeof obj === 'number' || typeof obj === 'boolean') {
    return obj;
  }
  
  // Default fallback for unknown types
  return String(obj);
}

export async function storeContractData(
  contractName: string,
  contractType: string,
  tokenName: string,
  contracts: AppliedValidators,
  txHash: string,
  walletAddress: string,
  lovelaceAmount: bigint,
  assets: Assets
): Promise<Prisma.ContractsCreateInput[]> {
  try {
    const contract: Prisma.ContractsCreateInput[] = [];

    await prisma.$executeRaw`
      INSERT INTO "Contracts" (
        "contractId",
        "contractName",
        "contractType",
        "contractAddress",
        "compiledCode",
        "tokenName",
        "lockTxHash",
        "active",
        "createdAt",
        "updatedAt"
      ) VALUES (
        ${contracts.policyId},
        ${contractName},
        ${contractType},
        ${contracts.lockAddress},
        ${contracts.giftCard},
        ${tokenName},
        ${txHash},
        ${true},
        ${new Date()},
        ${new Date()}
      )
      `;    

    const safeAssets = serializeBigInt(assets);
    const assetsJson = JSON.stringify(safeAssets);
    
    // Use raw SQL with a comma after "assets"
    await prisma.$executeRaw`
      INSERT INTO "Transactions" (
        "transactionId", 
        "contractId", 
        "from", 
        "to", 
        "value", 
        "assets",
        "timestamp", 
        "lockedInContract"
      ) VALUES (
        ${txHash}, 
        ${contracts.policyId}, 
        ${walletAddress}, 
        ${contracts.lockAddress}, 
        ${lovelaceAmount.toString()}::bigint, 
        ${assetsJson}::jsonb,
        ${new Date()}, 
        ${true}
      )
    `;
    
    console.log("Transaction inserted with ID:", txHash);
    
    return contract;
  } catch (error) {
    console.error("Error storing contract data:", error);
    throw new Error(`Failed to store contract data: ${error instanceof Error ? error.message : String(error)}`);
  }
}

export async function getContractByPolicyId(policyId: string) {
  try {
    // Query the Contracts table where contractId equals the policyId
    const contract = await prisma.contracts.findUnique({
      where: {
        contractId: policyId,
        active: true,
      },
    });
    
    return contract;
  } catch (error) {
    console.error("Error retrieving contract by policy ID:", error);
    throw error;
  }
}

export async function updateContractData(contractId: string) {
  try {
    // Update the contract to set active = false
    const updatedContract = await prisma.contracts.update({
      where: {
        contractId: contractId,
      },
      data: {
        active: false,
        updatedAt: new Date(),
      },
    });
    
    console.log(`Updated contract ${contractId} to active = false`);
    
    // Update all transactions associated with this contract to set lockedInContract = false
    const updatedTransactions = await prisma.transactions.updateMany({
      where: {
        contractId: contractId,
      },
      data: {
        lockedInContract: false,
      },
    });
    
    console.log(`Updated ${updatedTransactions.count} transactions for contract ${contractId} to lockedInContract = false`);
    
    return {
      success: true,
      message: `Contract ${contractId} and ${updatedTransactions.count} related transactions updated`,
      updatedContract,
    };
  } catch (error) {
    console.error(`Error updating contract data for ${contractId}:`, error);
    throw new Error(`Failed to update contract data: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Additional function to check a contract's status
export async function getContractStatus(contractId: string) {
  try {
    const contract = await prisma.contracts.findUnique({
      where: {
        contractId: contractId,
      },
      select: {
        active: true,
        contractName: true,
        contractType: true,
        transactions: {
          select: {
            lockedInContract: true,
            transactionId: true,
          },
        },
      },
    });
    
    if (!contract) {
      return {
        exists: false,
        message: `No contract found with ID ${contractId}`,
      };
    }
    
    return {
      exists: true,
      isActive: contract.active,
      contractName: contract.contractName,
      contractType: contract.contractType,
      transactions: contract.transactions,
      lockedTransactionsCount: contract.transactions.filter(t => t.lockedInContract).length,
    };
  } catch (error) {
    console.error(`Error checking contract status for ${contractId}:`, error);
    throw new Error(`Failed to check contract status: ${error instanceof Error ? error.message : String(error)}`);
  }
}