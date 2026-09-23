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
      <label htmlFor="product-search" className="field-label">
        Buscar no catálogo
      </label>
      <div className="search-row">
        <div className="search-input-wrapper">
          <span className="search-icon" aria-hidden="true" />
          <input
            id="product-search"
            name="product-search"
            type="search"
            value={value}
            placeholder="Digite o nome de um produto"
            onChange={(event) => setValue(event.target.value)}
          />
        </div>
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
