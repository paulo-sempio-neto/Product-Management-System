import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { PackagePlus, RotateCw, Search, ServerCrash, X } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { ApiRequestError, createProduct, deleteProduct } from "../api/products";
import { useAuth } from "../auth/AuthContext";
import CommandPalette from "../components/dashboard/CommandPalette";
import PaginationBar from "../components/dashboard/PaginationBar";
import ProductDrawer, { type DrawerState } from "../components/dashboard/ProductDrawer";
import ProductList, { ProductListSkeleton } from "../components/dashboard/ProductList";
import StatsStrip from "../components/dashboard/StatsStrip";
import Topbar from "../components/dashboard/Topbar";
import Button from "../components/ui/Button";
import Overlay from "../components/ui/Overlay";
import { useToast } from "../components/ui/Toast";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { PAGE_SIZE, useCatalog } from "../hooks/useCatalog";
import { formatPrice } from "../lib/format";
import type { Product } from "../types/product";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Bom dia";
  if (hour < 18) return "Boa tarde";
  return "Boa noite";
}

export default function DashboardPage() {
  const { session, logout } = useAuth();
  const toast = useToast();
  const location = useLocation();
  const navigate = useNavigate();
  const reduce = useReducedMotion();
  const searchInput = useRef<HTMLInputElement>(null);

  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const search = useDebouncedValue(query.trim(), 300);
  const { data, stats, loading, error, refresh } = useCatalog(page, search);

  const [drawer, setDrawer] = useState<DrawerState>(null);
  const [confirming, setConfirming] = useState<Product | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [freshId, setFreshId] = useState<number | null>(null);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [slowServer, setSlowServer] = useState(false);
  const [arrival] = useState(() => Boolean((location.state as { welcome?: string } | null)?.welcome));

  useEffect(() => {
    document.title = "Produtos · Gôndola";
    if (arrival) navigate(location.pathname, { replace: true, state: null });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => setPage(1), [search]);

  // Render's free tier sleeps; tell people why the first load is slow.
  useEffect(() => {
    if (!loading) {
      setSlowServer(false);
      return;
    }
    const timer = window.setTimeout(() => setSlowServer(true), 4000);
    return () => window.clearTimeout(timer);
  }, [loading]);

  useEffect(() => {
    if (freshId === null) return;
    const timer = window.setTimeout(() => setFreshId(null), 2400);
    return () => window.clearTimeout(timer);
  }, [freshId]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        if (!drawer && !confirming) setPaletteOpen((value) => !value);
        return;
      }
      if (paletteOpen) return;
      const target = event.target as HTMLElement;
      const typing = target.closest("input, textarea, [contenteditable]");
      if (typing || drawer || confirming) return;
      if (event.key === "/") {
        event.preventDefault();
        searchInput.current?.focus();
      } else if (event.key.toLowerCase() === "n" && !event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        setDrawer({ mode: "create" });
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [drawer, confirming, paletteOpen]);

  const closeDrawer = useCallback(() => setDrawer(null), []);
  const closePalette = useCallback(() => setPaletteOpen(false), []);
  const openCreate = useCallback(() => setDrawer({ mode: "create" }), []);
  const openEdit = useCallback((product: Product) => setDrawer({ mode: "edit", product }), []);

  function handleSaved(product: Product, mode: "create" | "edit") {
    setDrawer(null);
    setFreshId(product.id);
    if (mode === "create") {
      setQuery("");
      setPage(1);
    }
    refresh();
    toast({
      tone: "success",
      title: mode === "create" ? "Produto cadastrado" : "Alterações salvas",
      description: `${product.name}, ${formatPrice(product.price)}`,
    });
  }

  async function handleDelete() {
    if (!confirming) return;
    const product = confirming;
    setDeleting(true);
    try {
      await deleteProduct(product.id);
      setConfirming(null);
      if (data.items.length === 1 && page > 1) setPage(page - 1);
      refresh();
      toast({
        tone: "success",
        title: "Produto excluído",
        description: product.name,
        action: {
          label: "Desfazer",
          onClick: async () => {
            try {
              const restored = await createProduct({ name: product.name, price: String(product.price) });
              setFreshId(restored.id);
              refresh();
              toast({ tone: "success", title: "Produto restaurado", description: `${restored.name} voltou com o código ${restored.id}.` });
            } catch {
              toast({ tone: "error", title: "Não foi possível restaurar", description: "Cadastre o produto de novo pelo botão Novo produto." });
            }
          },
        },
      });
    } catch (reason) {
      const gone = reason instanceof ApiRequestError && reason.status === 404;
      setConfirming(null);
      refresh();
      toast({
        tone: "error",
        title: gone ? "Este produto já tinha sido excluído" : "Não foi possível excluir",
        description: gone ? "A lista foi atualizada." : "Verifique a conexão e tente de novo.",
      });
    } finally {
      setDeleting(false);
    }
  }

  if (!session) return null;
  const firstName = session.user.name.split(" ")[0];
  const firstLoad = loading && data.items.length === 0 && !error;

  return (
    <div className="dash">
      <a className="skip-link" href="#conteudo">
        Pular para o conteúdo
      </a>
      <Topbar user={session.user} onLogout={logout} onOpenPalette={() => setPaletteOpen(true)} />

      <main id="conteudo" className="dash__main" tabIndex={-1}>
        <motion.section
          className="dash__hero"
          initial={reduce ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: arrival ? 0.45 : 0, ease: [0.22, 1, 0.36, 1] }}
        >
          <div>
            <p className="dash__greeting">
              {greeting()}, {firstName}
            </p>
            <h1>{session.user.storeName}</h1>
          </div>
          <Button size="lg" icon={<PackagePlus size={20} />} onClick={() => setDrawer({ mode: "create" })} aria-keyshortcuts="n">
            Novo produto
          </Button>
        </motion.section>

        <motion.div
          initial={reduce ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: arrival ? 0.55 : 0.08, ease: [0.22, 1, 0.36, 1] }}
        >
          <StatsStrip stats={stats} />
        </motion.div>

        <motion.section
          className="catalog"
          aria-labelledby="catalog-title"
          aria-busy={loading}
          initial={reduce ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: arrival ? 0.65 : 0.16, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="catalog__toolbar">
            <h2 id="catalog-title">Produtos</h2>
            <div className="search">
              <Search size={18} className="search__icon" aria-hidden="true" />
              <input
                ref={searchInput}
                type="search"
                className="search__input"
                placeholder="Buscar pelo nome"
                aria-label="Buscar produtos pelo nome"
                aria-keyshortcuts="/"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              {query ? (
                <button type="button" className="search__clear" onClick={() => setQuery("")} aria-label="Limpar busca">
                  <X size={16} />
                </button>
              ) : (
                <kbd className="search__kbd" aria-hidden="true">
                  /
                </kbd>
              )}
            </div>
          </div>

          <div className={`catalog__progress ${loading && !firstLoad ? "is-active" : ""}`} aria-hidden="true" />

          <AnimatePresence>
            {slowServer && (
              <motion.p className="notice notice--info" role="status" initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}>
                O servidor estava em repouso e está iniciando. A primeira resposta pode levar até um minuto.
              </motion.p>
            )}
          </AnimatePresence>

          {error && !loading ? (
            <div className="empty empty--error" role="alert">
              <span className="empty__icon" aria-hidden="true">
                <ServerCrash size={26} />
              </span>
              <h3>Não conseguimos carregar os produtos</h3>
              <p>{error}. Verifique sua conexão e tente de novo.</p>
              <Button variant="ghost" icon={<RotateCw size={16} />} onClick={refresh}>
                Tentar de novo
              </Button>
            </div>
          ) : firstLoad ? (
            <ProductListSkeleton />
          ) : (
            <ProductList
              products={data.items}
              loading={loading}
              search={search}
              freshId={freshId}
              onEdit={(product) => setDrawer({ mode: "edit", product })}
              onDelete={setConfirming}
              onCreate={() => setDrawer({ mode: "create" })}
              onClearSearch={() => setQuery("")}
            />
          )}

          {!error && <PaginationBar page={data.page} limit={data.limit || PAGE_SIZE} total={data.total} disabled={loading} onChange={setPage} />}
        </motion.section>
      </main>

      <CommandPalette open={paletteOpen} onClose={closePalette} onCreate={openCreate} onEdit={openEdit} onLogout={logout} />

      <ProductDrawer state={drawer} onClose={closeDrawer} onSaved={handleSaved} />

      <Overlay
        variant="dialog"
        tone="danger"
        open={confirming !== null}
        onClose={() => !deleting && setConfirming(null)}
        title={`Excluir “${confirming?.name ?? ""}”?`}
        description="O produto sai do catálogo. Você ainda pode desfazer logo em seguida."
        footer={
          <>
            <Button variant="quiet" onClick={() => setConfirming(null)} disabled={deleting} data-autofocus>
              Cancelar
            </Button>
            <Button variant="danger" loading={deleting} onClick={handleDelete}>
              Excluir produto
            </Button>
          </>
        }
      >
        {null}
      </Overlay>

      <AnimatePresence>
        {arrival && (
          <motion.div
            className="arrival-curtain"
            aria-hidden="true"
            initial={{ clipPath: "circle(150vmax at 50% 50%)" }}
            animate={{ clipPath: "circle(0px at 50% 50%)" }}
            transition={{ duration: reduce ? 0.01 : 0.75, ease: [0.65, 0, 0.35, 1], delay: 0.05 }}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
