// App principal - funções compartilhadas

// Atualizar indicador do carrinho no header
function updateCartIndicator() {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const total = cart.reduce((sum, item) => {
        let compTotal = item.complementos.reduce((s, c) => s + c.preco, 0);
        return sum + ((item.preco + compTotal) * item.quantidade);
    }, 0);
    
    const count = cart.reduce((sum, item) => sum + item.quantidade, 0);
    
    const cartCount = document.getElementById('cartCount');
    const cartTotal = document.getElementById('cartTotal');
    const cartFloat = document.getElementById('cartFloat');
    
    if (cartCount) cartCount.textContent = count;
    if (cartTotal) cartTotal.textContent = `R$ ${total.toFixed(2)}`;
    if (cartFloat) cartFloat.style.display = count > 0 ? 'flex' : 'none';
}

// Inicializar
document.addEventListener('DOMContentLoaded', function() {
    updateCartIndicator();
});

// Exportar funções para uso global
window.updateCartIndicator = updateCartIndicator;
