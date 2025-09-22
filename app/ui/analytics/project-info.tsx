import { Info } from "lucide-react";
import { Alert, AlertDescription } from "./ui/alert";

export const ProjectInfo = () => {
  return (
    <div className="bg-muted p-4 mt-auto">
      <Alert className="bg-muted text-muted-foreground border-0">
        <Info className="h-4 w-4 text-primary" />
        <AlertDescription>
          This application uses AI to query our database with Natural Language.
          It may take a few seconds to generate the SQL query and run it.
          And sometimes, just sometimes, makes mistakes!!!{" "}
        </AlertDescription>
      </Alert>
    </div>
  );
};
