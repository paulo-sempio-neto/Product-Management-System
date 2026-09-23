import { useEffect, useState } from "react";

import { listProducts } from "./api/products";
import Pagination from "./components/Pagination";
import ProductTable from "./components/ProductTable";
import SearchBar from "./components/SearchBar";
import type { ProductListResponse } from "./types/product";

const PAGE_SIZE = 20;

export default function App() {
  const [productsPage, setProductsPage] = useState<ProductListResponse>({
    items: [],
    page: 1,
    limit: PAGE_SIZE,
    total: 0,
  });
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let shouldIgnore = false;

    async function loadProducts() {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const result = await listProducts({
          page,
          limit: PAGE_SIZE,
          name: searchTerm || undefined,
        });

        if (!shouldIgnore) {
          setProductsPage(result);
        }
      } catch (error) {
        if (!shouldIgnore) {
          const message =
            error instanceof Error
              ? error.message
              : "Não foi possível carregar os produtos.";
          setErrorMessage(message);
        }
      } finally {
        if (!shouldIgnore) {
          setIsLoading(false);
        }
      }
    }

    void loadProducts();

    return () => {
      shouldIgnore = true;
    };
  }, [page, searchTerm]);

  function handleSearch(term: string) {
    setSearchTerm(term);
    setPage(1);
  }

  return (
    <main className="app-shell">
      <section className="page-header">
        <p className="eyebrow">Product Management System</p>
        <div>
          <h1>Produtos</h1>
          <p>
            Listagem inicial consumindo a API FastAPI com busca por nome e
            paginação.
          </p>
        </div>
      </section>

      <section className="content-card" aria-busy={isLoading}>
        <SearchBar
          initialValue={searchTerm}
          isLoading={isLoading}
          onSearch={handleSearch}
        />

        {isLoading && <p className="status-message">Carregando produtos...</p>}

        {errorMessage && !isLoading && (
          <p className="status-message error" role="alert">
            {errorMessage}
          </p>
        )}

        {!isLoading && !errorMessage && productsPage.items.length === 0 && (
          <p className="status-message">
            Nenhum produto encontrado
            {searchTerm ? ` para "${searchTerm}"` : ""}.
          </p>
        )}

        {!isLoading && !errorMessage && productsPage.items.length > 0 && (
          <ProductTable products={productsPage.items} />
        )}

        {!errorMessage && (
          <Pagination
            page={productsPage.page}
            limit={productsPage.limit}
            total={productsPage.total}
            isLoading={isLoading}
            onPageChange={setPage}
          />
        )}
      </section>
    </main>
  );
}
