/**
 * Cart listing and item components.
 */

import Vue from 'vue';

/**
 * Customer info form for a store order.
 */
Vue.component('store-cart-item', {
    template: require('!raw-loader!./store_cart_item.html'),
    props: {
        item: Object,
        readOnly: Boolean,
        changeItemCount: Function,
        removeItemFromCart: Function
    },
    methods: {
        /**
         * Calculates subtotal for a specific cart item, considering discounts, etc.
         * @param {Object} cartItem - Existing cart item
         * @return {number} - Subtotal for the item and its count in the cart
         */
        getSubtotal(cartItem) {
            let multiplier = 1;
            let qtyThresh = cartItem.product.discount_amount;
            let discountFactor = (100 - cartItem.product.discount_percentage) / 100;
            if(qtyThresh && cartItem.count >= qtyThresh) {
                multiplier *= discountFactor;
            }
            return cartItem.product.price * cartItem.count * multiplier;
        }
    }
});
