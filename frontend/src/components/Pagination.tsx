type PaginationProps = {
  page: number;
  limit: number;
  total: number;
  isLoading: boolean;
  onPageChange: (page: number) => void;
};

export default function Pagination({
  page,
  limit,
  total,
  isLoading,
  onPageChange,
}: PaginationProps) {
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const canGoPrevious = page > 1;
  const canGoNext = page < totalPages;

  return (
    <nav className="pagination" aria-label="Paginação de produtos">
      <button
        type="button"
        className="secondary"
        disabled={!canGoPrevious || isLoading}
        onClick={() => onPageChange(page - 1)}
      >
        Página anterior
      </button>

      <span>
        Página {page} de {totalPages} · {total} produto
        {total === 1 ? "" : "s"}
      </span>

      <button
        type="button"
        className="secondary"
        disabled={!canGoNext || isLoading}
        onClick={() => onPageChange(page + 1)}
      >
        Próxima página
      </button>
    </nav>
  );
}
