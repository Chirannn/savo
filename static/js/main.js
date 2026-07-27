/* Savo Mart Main JavaScript Functions */

document.addEventListener('DOMContentLoaded', () => {
  initWishlistToggles();
  initQuickViewModal();
  initToastAutoDismiss();
});

// Toast notification trigger
function showToast(message, type = 'success') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-msg toast-${type}`;
  toast.innerHTML = `
    <i class="fa-solid ${type === 'success' ? 'fa-circle-check text-green' : 'fa-circle-exclamation text-orange'}"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function initToastAutoDismiss() {
  const existingToasts = document.querySelectorAll('.toast-msg');
  existingToasts.forEach(toast => {
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });
}

// Wishlist AJAX toggle
function initWishlistToggles() {
  document.querySelectorAll('.wishlist-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      if (!productId) return;

      fetch(`/wishlist/toggle/${productId}/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      .then(res => {
        if (res.redirected) {
          window.location.href = res.url;
          return;
        }
        return res.json();
      })
      .then(data => {
        if (data && data.success) {
          if (data.added) {
            this.classList.add('active');
            this.querySelector('i').className = 'fa-solid fa-heart';
          } else {
            this.classList.remove('active');
            this.querySelector('i').className = 'fa-regular fa-heart';
          }
          showToast(data.message);
          
          // Update header count badge if exists
          const badge = document.querySelector('.wishlist-badge-count');
          if (badge && data.count !== undefined) {
            badge.textContent = data.count;
          }
        }
      })
      .catch(err => console.error('Wishlist toggle error:', err));
    });
  });
}

// Quick View Modal
function initQuickViewModal() {
  const modalBackdrop = document.getElementById('quickview-modal');
  const modalBox = document.getElementById('quickview-content');
  if (!modalBackdrop || !modalBox) return;

  document.querySelectorAll('.quickview-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      const productId = this.dataset.productId;
      
      modalBox.innerHTML = `
        <div style="padding: 4rem; text-align: center;">
          <i class="fa-solid fa-spinner fa-spin fa-2x text-green"></i>
          <p style="margin-top: 1rem;">Loading product details...</p>
        </div>
      `;
      modalBackdrop.classList.add('active');

      fetch(`/api/quickview/${productId}/`)
        .then(res => res.json())
        .then(data => {
          modalBox.innerHTML = `
            <button class="modal-close-btn" onclick="closeQuickView()"><i class="fa-solid fa-xmark"></i></button>
            <div class="quickview-grid">
              <div style="background: white; padding: 1.5rem; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                <img src="${data.image_url}" alt="${data.name}" style="max-height: 280px; object-fit: contain;">
              </div>
              <div style="display: flex; flex-direction: column; justify-content: center;">
                <span class="badge badge-green" style="align-self: flex-start; margin-bottom: 0.5rem;">${data.category}</span>
                <h2 style="font-size: 1.5rem; margin-bottom: 0.5rem;">${data.name}</h2>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1rem;">Unit Size: <strong>${data.unit}</strong></p>
                
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                  <span style="font-size: 1.6rem; font-weight: 700; color: var(--primary-green);">₹${data.effective_price}</span>
                  ${data.discount_price ? `<span style="text-decoration: line-through; color: #9CA3AF; font-size: 1.1rem;">₹${data.price}</span>` : ''}
                  ${data.discount_percent ? `<span class="badge badge-orange">-${data.discount_percent}% OFF</span>` : ''}
                </div>

                <p style="font-size: 0.92rem; color: var(--text-dark); margin-bottom: 1.5rem;">${data.description}</p>
                
                <form action="/cart/add/${data.id}/" method="POST" class="ajax-add-cart-form" style="display: flex; gap: 1rem; align-items: center;">
                  <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                  <div style="display: flex; align-items: center; border: 1.5px solid var(--border-color); border-radius: 8px; overflow: hidden;">
                    <button type="button" style="padding: 0.5rem 0.8rem; background: #F3F4F6;" onclick="this.nextElementSibling.stepDown()"><i class="fa-solid fa-minus"></i></button>
                    <input type="number" name="quantity" value="1" min="1" max="${data.stock}" style="width: 50px; text-align: center; border: none; font-weight: 600;">
                    <button type="button" style="padding: 0.5rem 0.8rem; background: #F3F4F6;" onclick="this.previousElementSibling.stepUp()"><i class="fa-solid fa-plus"></i></button>
                  </div>
                  <button type="submit" class="btn btn-primary" style="flex: 1;"><i class="fa-solid fa-basket-shopping"></i> Add to Cart</button>
                </form>
              </div>
            </div>
          `;
          attachAjaxAddCart();
        })
        .catch(err => {
          modalBox.innerHTML = `<div style="padding: 3rem; text-align: center; color: red;">Failed to load product details.</div>`;
        });
    });
  });
}

function closeQuickView() {
  const modalBackdrop = document.getElementById('quickview-modal');
  if (modalBackdrop) modalBackdrop.classList.remove('active');
}

function attachAjaxAddCart() {
  document.querySelectorAll('.ajax-add-cart-form').forEach(form => {
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const actionUrl = this.action;
      const formData = new FormData(this);

      fetch(actionUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast(data.message);
          const badge = document.querySelector('.cart-badge-count');
          if (badge && data.cart_count !== undefined) {
            badge.textContent = data.cart_count;
          }
          closeQuickView();
        }
      })
      .catch(err => console.error(err));
    });
  });
}

// CSRF Token Helper
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
