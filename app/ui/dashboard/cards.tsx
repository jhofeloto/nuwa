import { fetchCardData, fetchProjectById } from '@/app/lib/queries/queries';
import PerformanceCard from './projects/performance-card';


export default async function CardWrapper({ projectId }: { projectId?: string }) {
  let data;
  if (projectId) {
    data = await fetchProjectById(projectId);
  } else {
    data = await fetchCardData();
  }

  const {
    totalImpact,
    totalInvestment,
    totalBankableInvestment,
    totalIncome,
    landNumber,
    totalco2,
    area,
    averageCo2Total,
    sumCo2Total,
    projectName
  } = data;
  
  const performanceData = {
    projectId,
    projectName,
    totalImpact,
    totalInvestment,
    totalBankableInvestment,
    totalIncome,
    landNumber,
    totalco2,
    area,
    averageCo2Total,
    sumCo2Total,
  }

  return (
    <>

      
      <div className="grid gap-6">
        <PerformanceCard data={performanceData} />
      </div>
    </>
  );
}