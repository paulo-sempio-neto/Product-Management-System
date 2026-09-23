import type { Product } from "../types/product";

type ProductTableProps = {
  products: Product[];
};

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

export default function ProductTable({ products }: ProductTableProps) {
  return (
    <div className="table-wrapper">
      <table className="product-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Preço</th>
            <th>Versão</th>
          </tr>
        </thead>
        <tbody>
          {products.map((product) => (
            <tr key={product.id}>
              <td>{product.id}</td>
              <td>{product.name}</td>
              <td>{currencyFormatter.format(product.price)}</td>
              <td>{product.version}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
