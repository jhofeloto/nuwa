import { BarDatum } from "@nivo/bar";

import { 
  MoveIcon,
  DoubleArrowDownIcon,
  ColorWheelIcon,
  EnterIcon,
  CircleIcon,
  DoubleArrowRightIcon,
  AlignBaselineIcon,
  OpacityIcon
} from "@radix-ui/react-icons";
import { Flex } from "@radix-ui/themes";

import type {
  MintingPolicy,
  SpendingValidator
} from "@/app/lib/lucid-client";

// Define IconProps type manually
export type IconProps = {
  width?: number;
  height?: number;
  style?: React.CSSProperties;
};

export type User = {
  id: string;
  name: string;
  email: string;
  password: string;
};

export interface SpeciesValues {
  max_height: number | null; 
  wood_density: number | null; 
  growth_rate: string | null; 
  avg_dbh: number | null; 
  allometric_coeff_a: number | null; 
  allometric_coeff_b: number | null; 
  r_coeff: number | null; 
  g_b: number | null; 
  g_c: number | null; 
  g_b_dbh: number | null; 
  g_c_dbh: number | null; 
  k: number | null; 
  inflexion: number | null; 
  k2: string | null; 
  t_inflexion: string | null; 
  }

export interface EcosystemValues {
  BD: number | null;
  C: number | null;
  Profundidad: number | null;
  SOC: number | null;
  }

export interface CoverageValues {
  range: string | null;
  biomass_type: number | null;
  agb_equation: string | null;
  }

export interface ParcelAnalysisValues {
  ndvi_before: number | null, 
  ndvi_after: number | null, 
  biomassha_before: number | null, 
  biomassha_after: number | null, 
  url_geojson: string | null, 
  band11: string | null, 
  band4: string | null, 
  band3: string | null, 
  band8: string | null, 
  method: string | null, 
  time_horizon: number | null, 
  biomass_prediction: number | null, 
  ndvi_prediction: number | null, 
  }

// ✅ Helper function to structure values with units for Projects
export interface ProjectValues {
  impact: number | null;
  total_investment: number | null;
  bankable_investment: number | null;
  income: number | null;
  areaC1: number | null;
  areaC2: number | null;
  income_other: number | null;
  term: number | null;
  lands: number | null;
  abstract: string | null;
  investment_teaser: string | null;
  geolocation_point: string | null;
  polygone: string | null;
  tree_quantity: number | null;
  token_granularity: number | null;
  }

export interface ParcelData {
    project: string;
    department: string;
    ecosystem: string;
    species: string;
    parcelname: string;
    parcelId: string;
    area: number;
  }
  
export interface TreeNode {
    name: string;
    loc?: number;
    children?: TreeNode[];
    total?: number;
  }

export interface NavigationItem {
    name: string;
    href: string;
    current: boolean;
    subLinks?: { name: string; href: string }[];
}

export interface EcosystemData extends BarDatum {
  ecosystem: string;
  bgb: number;
  co2: number;
  agb: number;
  soc: number;
}

export interface PopulationResult extends BarDatum {
  period: number;
  population: number;
  co2eq_tonnes: number;
  co2eq_accumulated: number;
}

export interface Event {
  year: string;
  percentage: string;
}

export interface ParcelCo2Data {
  ecosystem: string;
  speceis: string;
  year: number;
  co2total: number;
}

export interface Breadcrumb {
  label: string;
  href: string;
  active?: boolean;
}

export interface LineChartProps {
  data: {
    id: string;
    data: { x: string | number; y: number }[];
  }[];
}

export interface GrowthData {
  species: string;
  year: number;
  co2eq: { toNumber: () => number } | number;
}

export const SpeciesUnitsMapping = {
  max_height: "m",
  wood_density: "g/cm³",
  growth_rate: "-",
  avg_dbh: "cm",
  allometric_coeff_a: "-",
  allometric_coeff_b: "-",
  r_coeff: "-",
  g_b: "m",
  g_c: "m",
  g_b_dbh: "kg?",
  g_c_dbh: "kg?",
  k: "years⁻¹",
  inflexion: "?",
  k2: "years⁻¹-range",
  t_inflexion: "year-range",
};

// ✅ Helper function to structure values with units for Ecosystems
// Ecosystem units mapping
export const EcosystemUnitsMapping = {
  BD: "g/cm³",
  C: "%",
  Profundidad: "m",
  SOC: "tC/ha",
};

export const CoverageUnitsMapping = {
  range: "-",
  biomass_type: "%",
  agb_equation: "-",
};

export const ParcelAnalysisUnitsMapping = {
  ndvi_before: "-", 
  ndvi_after: "-", 
  biomassha_before: "-", 
  biomassha_after: "-", 
  url_geojson: "-", 
  band11: "-", 
  band4: "-", 
  band3: "-", 
  band8: "-", 
  method: "-", 
  time_horizon: "-", 
  biomass_prediction: "-", 
  ndvi_prediction: "-",
};

// Projects units mapping
export const ProjectUnitsMapping = {
  impact: "tCO2e",
  total_investment: "USD",
  bankable_investment: "USD",
  income: "USD",
  areaC1: "Ha",
  areaC2: "Ha",
  income_other: "USD",
  term: "years",
  lands: "-", // No unit
  tree_quantity: "-",
  token_granularity: "-",
};

export type TotalImpactResult = { total_impact: bigint };
export type TotalInvestmentResult = { total_investment: bigint };
export type TotalBankableInvestmentResult = { total_bankable_investment: bigint };
export type TotalIncomeResult = { total_income: bigint };
export type CellValue = string | number | boolean | Date | null;

export type State = { species?: string; errors?: { species?: string[] } };

export type Growth = {
  id: string
  name: string
  title: string
  description: string | null
  country: string | null
  status: string
  department: string | null
  values: {
    total_investment: {
      value: number
    },
    impact: {
      value: number
    },
    bankable_investment: {
      value: number
    },
    income: {
      value: number
    },
    tree_quantity: {
      value: number
    },
    lands: {
      value: number
    },
    abstract: {
      value: string
    },
    polygone: {
      value: string
    },
    geolocation_point: {
      value: string
    },
    investment_teaser: {
      value: string
    },
    token_granularity: {
      value: number
    },
  }
  createdAt: Date
  updatedAt: Date
}

export type LayoutProps = React.ComponentPropsWithoutRef<typeof Flex> & {
  focusable?: boolean;
  data: {
      projectId: string | undefined;
      projectName: string;
      totalImpact: number;
      totalInvestment: number;
      totalBankableInvestment: number;
      totalIncome: number;
      landNumber: number;
      totalco2: number;
      area: number;
      averageCo2Total: number;
      sumCo2Total: number
  };
};

export interface HoverMessage {
    icon: React.ForwardRefExoticComponent<IconProps & React.RefAttributes<SVGSVGElement>>;
    title: string;
    content: string;
}

export const hoverMessages: Record<string, HoverMessage> = {
    impact: {
        icon: MoveIcon,
        title: "Impact",
        content: "Impact in the context of carbon credit projects refers to the measurable positive effects that these projects have on reducing greenhouse gas emissions, enhancing biodiversity, and supporting sustainable development in local communities. These impacts are quantified and verified to ensure that the projects contribute to mitigating climate change and promoting environmental and social benefits."
    },
    investment: {
        icon: DoubleArrowDownIcon,
        title: "Investment",
        content: "Investment refers to the total amount of financial resources allocated to the carbon credit projects. This includes funds used for project development, implementation, and maintenance to ensure the successful generation of carbon credits."
    },
    bankable: {
        icon: ColorWheelIcon,
        title: "Bankable",
        content: "Bankable investment refers to the portion of the total investment that is expected to generate a return. This is the amount that can be financed through loans or other financial instruments, based on the projected income from the sale of carbon credits."
    },
    income: {
        icon: EnterIcon,
        title: "Income",
        content: "Income refers to the revenue generated from the sale of carbon credits. This income is used to cover project costs and provide returns to investors, ensuring the financial sustainability of the carbon credit projects."
    },
    lands: {
        icon: CircleIcon,
        title: "Lands",
        content: "Lands refer to the total area of land involved in the carbon credit projects. This includes the areas where trees are planted, conserved, or managed to generate carbon credits."
    },
    totalco2eq: {
        icon: DoubleArrowRightIcon,
        title: "TotalCO2eq",
        content: "Total CO2 equivalent (CO2eq) represents the total amount of greenhouse gases reduced or sequestered by the carbon credit projects, expressed in terms of the equivalent amount of CO2."
    },
    area: {
        icon: AlignBaselineIcon,
        title: "Area",
        content: "Area refers to the total land area measured in hectares (Ha) that is involved in the carbon credit projects."
    },
    co2eq: {
        icon: MoveIcon,
        title: "CO2eq",
        content: "CO2 equivalent (CO2eq) per hectare represents the amount of greenhouse gases reduced or sequestered per hectare of land involved in the carbon credit projects."
    },
    co2eq_year: {
        icon: OpacityIcon,
        title: "CO2eq Year",
        content: "CO2 equivalent (CO2eq) per hectare per year represents the amount of greenhouse gases reduced or sequestered per hectare of land per year involved in the carbon credit projects."
    },
    area_tokens: {
        icon: AlignBaselineIcon,
        title: "Area Tokens",
        content: "Area Tokens represent the tokenized units of land area involved in the carbon credit projects, used for tracking and trading purposes."
    },
    token_value: {
        icon: DoubleArrowDownIcon,
        title: "Token Value",
        content: "Token Value represents the value of each tokenized unit of land area in terms of the amount of CO2 equivalent (CO2eq) it represents."
    },
    token_value_total: {
        icon: DoubleArrowRightIcon,
        title: "Token Value Total",
        content: "Token Value Total represents the total value of all tokenized units of land area in terms of the total amount of CO2 equivalent (CO2eq) they represent."
    },
    default: {
        icon: MoveIcon,
        title: "Default",
        content: "No specific information available for this indicator."
    }
};

export interface UseCardanoReturn {
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  stakeAddress: string | null;
  accountBalance: string | null;
  installedExtensions: string[];
  enabledWallet: string | null;
  usedAddresses: string[];
}

export type AppliedValidators = {
  redeem: SpendingValidator;
  giftCard: MintingPolicy;
  policyId: string;
  lockAddress: string;
};