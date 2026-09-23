import type { Product } from "../types/product";

type ProductTableProps = {
  products: Product[];
  onEdit: (product: Product) => void;
  onDelete: (product: Product) => void;
  deletingProductId: number | null;
};

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

export default function ProductTable({
  products,
  onEdit,
  onDelete,
  deletingProductId,
}: ProductTableProps) {
  return (
    <div className="table-wrapper">
      <table className="product-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Preço</th>
            <th>Versão</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.id}</td>
              <td>{product.name}</td>
              <td>{currencyFormatter.format(product.price)}</td>
              <td>{product.version}</td>
              <td>
                <div className="table-actions">
                  <button
                    type="button"
                    className="secondary compact"
                    disabled={deletingProductId === product.id}
                    onClick={() => onEdit(product)}
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    className="danger compact"
                    disabled={deletingProductId === product.id}
                    onClick={() => onDelete(product)}
                  >
                    {deletingProductId === product.id
                      ? "Excluindo..."
                      : "Excluir"}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
