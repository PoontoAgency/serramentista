/**
 * CatalogPage.tsx — Pagina principale catalogo prodotti e voci extra
 */
import { useState } from 'react';
import { useProducts, useCategories, useCreateProduct, useUpdateProduct, useDeleteProduct } from './useCatalog';
import type { Product } from './catalogService';
import ProductForm from './ProductForm';
import CategoryManager from './CategoryManager';
import TierPriceTable from './TierPriceTable';
import ExtraPresetsManager from './ExtraPresetsManager';
import './catalog.css';

type Tab = 'products' | 'categories' | 'extras';

export default function CatalogPage() {
  const [activeTab, setActiveTab] = useState<Tab>('products');
  const [filterTier, setFilterTier] = useState<string>('');
  const [filterCategory, setFilterCategory] = useState<string>('');
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  const { data: products = [], isLoading: productsLoading } = useProducts(
    filterTier || filterCategory
      ? { tier: filterTier || undefined, category_id: filterCategory || undefined }
      : undefined
  );
  const { data: categories = [] } = useCategories();
  const createProduct = useCreateProduct();
  const updateProduct = useUpdateProduct();
  const deleteProduct = useDeleteProduct();

  const handleProductSubmit = (data: any) => {
    if (editingProduct) {
      updateProduct.mutate({ id: editingProduct.id, ...data }, {
        onSuccess: () => { setEditingProduct(null); setShowForm(false); },
      });
    } else {
      createProduct.mutate(data, {
        onSuccess: () => setShowForm(false),
      });
    }
  };

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('Disattivare questo prodotto?')) {
      deleteProduct.mutate(id);
    }
  };

  return (
    <div className="catalog-page">
      <div className="catalog-header">
        <h2>📦 Catalogo</h2>
        <p className="catalog-subtitle">
          Gestisci i tuoi prodotti, categorie e voci extra
        </p>
      </div>

      {/* Tabs */}
      <div className="catalog-tabs">
        <button className={`tab ${activeTab === 'products' ? 'active' : ''}`}
                onClick={() => setActiveTab('products')}>
          Prodotti ({products.length})
        </button>
        <button className={`tab ${activeTab === 'categories' ? 'active' : ''}`}
                onClick={() => setActiveTab('categories')}>
          Categorie ({categories.length})
        </button>
        <button className={`tab ${activeTab === 'extras' ? 'active' : ''}`}
                onClick={() => setActiveTab('extras')}>
          Voci extra
        </button>
      </div>

      {/* Tab: Prodotti */}
      {activeTab === 'products' && (
        <div className="tab-content">
          <div className="products-toolbar">
            <div className="filters">
              <select value={filterTier} onChange={e => setFilterTier(e.target.value)}>
                <option value="">Tutte le fasce</option>
                <option value="base">🟢 Base</option>
                <option value="medio">🟡 Medio</option>
                <option value="top">🔴 Top</option>
              </select>
              <select value={filterCategory} onChange={e => setFilterCategory(e.target.value)}>
                <option value="">Tutte le categorie</option>
                {categories.map(c => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>
            {!showForm && (
              <button onClick={() => { setEditingProduct(null); setShowForm(true); }}
                      className="btn-primary">
                + Nuovo prodotto
              </button>
            )}
          </div>

          {showForm && (
            <div className="product-form-wrapper">
              <ProductForm
                product={editingProduct}
                categories={categories}
                onSubmit={handleProductSubmit}
                onCancel={() => { setShowForm(false); setEditingProduct(null); }}
                isLoading={createProduct.isPending || updateProduct.isPending}
              />
            </div>
          )}

          {productsLoading ? (
            <div className="loading">Caricamento prodotti...</div>
          ) : (
            <TierPriceTable products={products} onEdit={handleEdit} onDelete={handleDelete} />
          )}
        </div>
      )}

      {/* Tab: Categorie */}
      {activeTab === 'categories' && (
        <div className="tab-content">
          <CategoryManager />
        </div>
      )}

      {/* Tab: Voci extra */}
      {activeTab === 'extras' && (
        <div className="tab-content">
          <ExtraPresetsManager />
        </div>
      )}
    </div>
  );
}
