
export const Header = ({ handleClear }: { handleClear: () => void }) => {

  return (
    <div className="flex items-center justify-between mb-6">
      <h1
        className="text-2xl sm:text-3xl font-bold text-foreground flex items-center cursor-pointer"
        onClick={() => handleClear()}
      >
        Data analysis with Natural Language
      </h1>
    </div>
  );
};
