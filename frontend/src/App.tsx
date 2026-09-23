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

      <section className="content-card">
        <ProductForm
          isSubmitting={isCreating}
          errorMessage={createErrorMessage}
          successMessage={createSuccessMessage}
          onSubmit={handleCreateProduct}
        />
      </section>

      {editingProduct && (
        <section className="content-card">
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

      <section className="content-card" aria-busy={isLoading}>
        <div className="section-heading">
          <h2>Lista de produtos</h2>
          <p>Consulte produtos cadastrados com busca por nome e paginação.</p>
        </div>

        <SearchBar
          initialValue={searchTerm}
          isLoading={isLoading}
          onSearch={handleSearch}
        />

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
  );
}
