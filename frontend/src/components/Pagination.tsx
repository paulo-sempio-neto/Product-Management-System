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
        <span aria-hidden="true">←</span> Anterior
      </button>

      <div className="pagination-summary">
        <strong>
          Página {page} de {totalPages}
        </strong>
        <span>
          {total} produto{total === 1 ? "" : "s"} no total
        </span>
      </div>

      <button
        type="button"
        className="secondary"
        disabled={!canGoNext || isLoading}
        onClick={() => onPageChange(page + 1)}
      >
        Próxima <span aria-hidden="true">→</span>
      </button>
    </nav>
  );
}
