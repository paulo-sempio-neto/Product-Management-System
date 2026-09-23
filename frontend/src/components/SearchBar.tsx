import { type FormEvent, useState } from "react";

type SearchBarProps = {
  initialValue: string;
  isLoading: boolean;
  onSearch: (term: string) => void;
};

export default function SearchBar({
  initialValue,
  isLoading,
  onSearch,
}: SearchBarProps) {
  const [value, setValue] = useState(initialValue);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSearch(value.trim());
  }

  function handleClear() {
    setValue("");
    onSearch("");
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <label htmlFor="product-search">Buscar por nome</label>
      <div className="search-row">
        <input
          id="product-search"
          name="product-search"
          type="search"
          value={value}
          placeholder="Ex.: arroz"
          onChange={(event) => setValue(event.target.value)}
        />
        <button type="submit" disabled={isLoading}>
          Buscar
        </button>
        <button type="button" className="secondary" onClick={handleClear}>
          Limpar
        </button>
      </div>
    </form>
  );
}
