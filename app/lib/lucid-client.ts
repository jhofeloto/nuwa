
// ✅ Safe type-only imports
export type {
    Cardano,
    MintingPolicy,
    OutRef,
    SpendingValidator,
    LucidEvolution,
    Lucid,
  } from "@lucid-evolution/lucid";
  
  // 🔵 Utility types
  import type {
    applyDoubleCborEncoding as applyDoubleCborEncodingType,
    applyParamsToScript as applyParamsToScriptType,
    fromText as fromTextType,
    fromHex as fromHexType,
    validatorToAddress as validatorToAddressType,
    validatorToScriptHash as validatorToScriptHashType,
    Blockfrost as BlockfrostType,
    Lucid as LucidType
  } from "@lucid-evolution/lucid";

  
  export type WASMHelpers = {
    Constr: typeof import("@lucid-evolution/lucid").Constr;
    Data: typeof import("@lucid-evolution/lucid").Data;
    Lucid: typeof LucidType;
    Blockfrost: typeof BlockfrostType;
    fromText: typeof fromTextType;
    fromHex: typeof fromHexType;
    applyParamsToScript: typeof applyParamsToScriptType;
    applyDoubleCborEncoding: typeof applyDoubleCborEncodingType;
    validatorToAddress: typeof validatorToAddressType;
    validatorToScriptHash: typeof validatorToScriptHashType;
  };
  
  /**
   * Lazy-load CML-bound objects safely (Constr, Data, Lucid)
   */
  export const getLucidWasmBindings = async (): Promise<WASMHelpers> => {
    if (typeof window === "undefined") {
      throw new Error("Lucid WASM helpers can only be used client-side");
    }

    const lucid = await import("@lucid-evolution/lucid");

    if (!lucid.Constr) {
        throw new Error("Failed to initialize Lucid WASM");
      }
  
    const { Constr, Data, Lucid, Blockfrost, fromText, fromHex, applyParamsToScript, applyDoubleCborEncoding, validatorToAddress, validatorToScriptHash } = await import("@lucid-evolution/lucid");
  
    return { Constr, Data, Lucid, Blockfrost, fromText, fromHex, applyParamsToScript, applyDoubleCborEncoding, validatorToAddress, validatorToScriptHash };
  };
  