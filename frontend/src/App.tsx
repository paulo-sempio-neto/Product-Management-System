import { useEffect, useState } from "react";

import {
  ApiRequestError,
  createProduct,
  deleteProduct,
  listProducts,
  updateProduct,
} from "./api/products";
import Pagination from "./components/Pagination";
import ProductEditForm from "./components/ProductEditForm";
import ProductForm from "./components/ProductForm";
import ProductTable from "./components/ProductTable";
import SearchBar from "./components/SearchBar";
import type {
  Product,
  ProductCreateInput,
  ProductListResponse,
  ProductUpdateInput,
} from "./types/product";

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
  const [refreshKey, setRefreshKey] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [createErrorMessage, setCreateErrorMessage] = useState<string | null>(
    null,
  );
  const [createSuccessMessage, setCreateSuccessMessage] = useState<
    string | null
  >(null);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateErrorMessage, setUpdateErrorMessage] = useState<string | null>(
    null,
  );
  const [updateSuccessMessage, setUpdateSuccessMessage] = useState<
    string | null
  >(null);
  const [deletingProductId, setDeletingProductId] = useState<number | null>(
    null,
  );
  const [deleteMessage, setDeleteMessage] = useState<string | null>(null);
  const [deleteErrorMessage, setDeleteErrorMessage] = useState<string | null>(
    null,
  );

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
  }, [page, refreshKey, searchTerm]);

  function handleSearch(term: string) {
    setSearchTerm(term);
    setPage(1);
  }

  async function handleCreateProduct(
    input: ProductCreateInput,
  ): Promise<boolean> {
    setIsCreating(true);
    setCreateErrorMessage(null);
    setCreateSuccessMessage(null);

    try {
      const createdProduct = await createProduct(input);
      setCreateSuccessMessage(
        `Produto "${createdProduct.name}" criado com sucesso.`,
      );
      setRefreshKey((current) => current + 1);
      return true;
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : "Não foi possível criar o produto.";
      setCreateErrorMessage(message);
      return false;
    } finally {
      setIsCreating(false);
    }
  }

  function handleSelectProductToEdit(product: Product) {
    setEditingProduct(product);
    setUpdateErrorMessage(null);
    setUpdateSuccessMessage(null);
  }

  function handleCancelEdit() {
    setEditingProduct(null);
    setUpdateErrorMessage(null);
    setUpdateSuccessMessage(null);
  }

  async function handleUpdateProduct(
    input: ProductUpdateInput,
  ): Promise<boolean> {
    if (!editingProduct) {
      return false;
    }

    setIsUpdating(true);
    setUpdateErrorMessage(null);
    setUpdateSuccessMessage(null);

    try {
      const updatedProduct = await updateProduct(editingProduct.id, input);
      setEditingProduct(updatedProduct);
      setUpdateSuccessMessage(
        `Produto "${updatedProduct.name}" atualizado com sucesso.`,
      );
      setRefreshKey((current) => current + 1);
      return true;
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 409) {
        setUpdateErrorMessage(
          "Este produto foi alterado por outra operação. Recarregue a listagem e tente novamente.",
        );
      } else if (error instanceof ApiRequestError && error.status === 404) {
        setUpdateErrorMessage(
          "Produto não encontrado. Ele pode ter sido removido por outra operação.",
        );
      } else {
        const message =
          error instanceof Error
            ? error.message
            : "Não foi possível atualizar o produto.";
        setUpdateErrorMessage(message);
      }

      return false;
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleDeleteProduct(product: Product) {
    const shouldDelete = window.confirm(
      `Tem certeza que deseja excluir o produto "${product.name}"?`,
    );

    if (!shouldDelete) {
      return;
    }

    setDeletingProductId(product.id);
    setDeleteMessage(null);
    setDeleteErrorMessage(null);

    try {
      await deleteProduct(product.id);
      setDeleteMessage(`Produto "${product.name}" excluído com sucesso.`);

      if (editingProduct?.id === product.id) {
        handleCancelEdit();
      }

      const isLastItemOnPage = productsPage.items.length === 1;
      const shouldGoBackOnePage = page > 1 && isLastItemOnPage;

      if (shouldGoBackOnePage) {
        setPage((current) => current - 1);
      } else {
        setRefreshKey((current) => current + 1);
      }
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 404) {
        setDeleteErrorMessage(
          "Produto não encontrado. Ele pode já ter sido removido por outra operação.",
        );
        setRefreshKey((current) => current + 1);
      } else {
        const message =
          error instanceof Error
            ? error.message
            : "Não foi possível excluir o produto.";
        setDeleteErrorMessage(message);
      }
    } finally {
      setDeletingProductId(null);
    }
  }

  return (
    <div className="app-shell">
      <header className="page-header">
        <div className="brand-row">
          <span className="brand-mark" aria-hidden="true">
            PM
          </span>
          <div>
            <p className="eyebrow">Product Management System</p>
            <p className="brand-caption">Painel administrativo</p>
          </div>
        </div>

        <div className="hero-layout">
          <div className="hero-copy">
            <span className="hero-kicker">Catálogo</span>
            <h1>Gestão de produtos</h1>
            <p>
              Cadastre, encontre e mantenha seu catálogo atualizado em uma
              interface conectada à API FastAPI.
            </p>
          </div>

          <div className="dashboard-summary" aria-label="Resumo do catálogo">
            <div className="summary-item">
              <strong>{productsPage.total}</strong>
              <span>produtos</span>
            </div>
            <div className="summary-divider" aria-hidden="true" />
            <div className="summary-item">
              <strong>{productsPage.page}</strong>
              <span>página atual</span>
            </div>
            <div className="summary-divider" aria-hidden="true" />
            <div className="summary-item">
              <strong>{PAGE_SIZE}</strong>
              <span>itens por página</span>
            </div>
          </div>
        </div>
      </header>

      <main className="dashboard-content">
        <section className="content-card create-card">
          <ProductForm
            isSubmitting={isCreating}
            errorMessage={createErrorMessage}
            successMessage={createSuccessMessage}
            onSubmit={handleCreateProduct}
          />
        </section>

        {editingProduct && (
          <section className="content-card edit-card">
            <ProductEditForm
              product={editingProduct}
              isSubmitting={isUpdating}
              errorMessage={updateErrorMessage}
              successMessage={updateSuccessMessage}
              onCancel={handleCancelEdit}
              onSubmit={handleUpdateProduct}
            />
          </section>
        )}

        <section className="content-card list-card" aria-busy={isLoading}>
          <div className="section-heading section-heading-inline">
            <div>
              <span className="section-kicker">Inventário</span>
              <h2>Produtos cadastrados</h2>
              <p>Use a busca para localizar rapidamente um item do catálogo.</p>
            </div>
            <span className="result-count">
              {productsPage.total} {productsPage.total === 1 ? "item" : "itens"}
            </span>
          </div>

          <div className="list-toolbar">
            <SearchBar
              initialValue={searchTerm}
              isLoading={isLoading}
              onSearch={handleSearch}
            />
          </div>

          <div className="feedback-region" aria-live="polite">
            {deleteMessage && (
              <p className="status-message success" role="status">
                {deleteMessage}
              </p>
            )}

            {deleteErrorMessage && (
              <p className="status-message error" role="alert">
                {deleteErrorMessage}
              </p>
            )}
          </div>

          {isLoading && (
            <div className="status-message loading-state" role="status">
              <span className="loading-spinner" aria-hidden="true" />
              <span>
                <strong>Carregando produtos</strong>
                <small>Buscando os dados mais recentes do catálogo...</small>
              </span>
            </div>
          )}

          {errorMessage && !isLoading && (
            <div className="status-message error state-card" role="alert">
              <span className="state-icon" aria-hidden="true">
                !
              </span>
              <span>
                <strong>Não foi possível carregar os produtos</strong>
                <small>{errorMessage}</small>
              </span>
            </div>
          )}

          {!isLoading && !errorMessage && productsPage.items.length === 0 && (
            <div className="empty-state">
              <span className="empty-state-icon" aria-hidden="true" />
              <h3>Nenhum produto encontrado</h3>
              <p>
                {searchTerm
                  ? `Não encontramos resultados para "${searchTerm}". Tente outro termo.`
                  : "Cadastre o primeiro produto para começar a organizar seu catálogo."}
              </p>
            </div>
          )}

          {!isLoading && !errorMessage && productsPage.items.length > 0 && (
            <ProductTable
              products={productsPage.items}
              deletingProductId={deletingProductId}
              onEdit={handleSelectProductToEdit}
              onDelete={handleDeleteProduct}
            />
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
    </div>
  );
}
