/* global $ */

import Vue from 'vue';

import {
    formatPrice,
    cartItemEquals,
    getDiscountedPrice,
} from './store_common.js';

/**
 * Displays a single store product with cart counts and "add" button.
 */
Vue.component('store-product', {
    template: require('./store_product.html'),
    props: {
        product: Object,
        cart: Array,
        messages: Object,
        changeItemCount: Function,
        removeItemFromCart: Function,
    },
    data() {
        // because there can be many components of the same type, a component's
        // "data" is a factory function that should return unique objects
        return {
            /** Currently selected item variant */
            variant: null,
        };
    },
    /**
     * Initialize the store product component, auto-selecting variant if available
     */
    created() {
        let product = this.product;
        if (product.variants && product.variants.length) {
            this.variant = product.variants[0];
        }
    },
    methods: {
        /**
         * Signal that a new item should be added to the cart.
         */
        addItem() {
            this.$emit('addItem', this.product, this.variant);
        },
        removeItem() {
            this.$emit('removeItem', this.product, this.variant);
        },
        /**
         * Gets current item + variant's count in the cart.
         * @returns {number} - Number of items in the cart
         */
        getCartCount() {
            const { product, variant } = this;
            if(!this.cart) {
                return 0;
            }
            let cartIndex = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });

            if(cartIndex < 0) {
                return 0;
            }
            return this.cart[cartIndex].count;
        },
        /**
         * Checks if the quantity discount applies to this product.
         * @returns {Boolean} - True if quantity discount is active
         */
        isDiscountActive() {
            const { product } = this;
            let discountAmount = product.discount_amount;
            return discountAmount > 0 && this.getCartCount() >= discountAmount;
        },
        /**
         * Returns the effective unit price of this product, considering discounts.
         * @returns {number} - Unit price
         */
        getEffectivePrice() {
            return getDiscountedPrice(this.product, this.getCartCount());
        },
        /**
         * Show full size image of the product.
         */
        showFullSize() {
            if (!this.product.imagefile_original_url) {
                return;
            }
            let thumbnail = $(this.$el).find('.product-thumbnail');
            $(thumbnail).ekkoLightbox();
        }
    },
    computed: {
        isOutOfStock() {
            return this.getCartCount() >= this.product.num_available;
        },
        effectivePrice() {
            return this.getEffectivePrice();
        },
        cartItems() {
            let items = [];
            this.cart.forEach((item) => {
                if(cartItemEquals(item, this.product)) {
                    items.push(item);
                }
            });
            return items;
        }
    }
});