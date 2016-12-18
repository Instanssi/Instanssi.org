/* global $ */

// IE11 support
import 'core-js/es6/array';
import 'core-js/es6/object';
import 'core-js/es6/promise';

import Vue from 'vue';
import { formatPrice, storeXHR, loadingOverlay } from './store_common.js';
import './store_information.js';
import './store_cart.js';

const PAYMENT_METHODS = [
    { id: 1, name: 'Paytrail verkkomaksu' },
    { id: 0, name: 'BitPay (maksa BitCoinilla)' }
];

/**
 * Gets the price of a certain quantity of a product, considering discounts, etc.
 * @param {Object} product - Product / StoreItem
 * @param {number} count - Number of items in cart
 * @returns {number} - Effective price
 */
function getDiscountedPrice(product, count) {
    let qtyThresh = product.discount_amount;
    let discountFactor = (100 - product.discount_percentage) / 100;
    let multiplier = 1;
    if(qtyThresh && count >= qtyThresh) {
        multiplier *= discountFactor;
    }
    return product.price * multiplier;
}

/**
 * Returns true if a cart item is a specific product (and optional variant).
 * @param {Object} cartItem - Cart item to compare
 * @param {Object} product - Product to compare
 * @param {Object} [variant] - Variant to compare
 * @returns {Boolean} - True if cart item is the same product (and variant)
 */
function cartItemEquals(cartItem, product, variant) {
    return cartItem.product.id === product.id &&
        (!variant || (cartItem.variant && (variant.id === cartItem.variant.id)));
}

/**
 * Fetch items from the store API.
 * @returns {Promise.<Object>} - API response
 */
function fetchItems() {
    return storeXHR('GET', '/api/store_items/?format=json');
}
/**
 * Submits a transaction to the store API.
 * @param {Object} transaction - Transaction data
 * @returns {Promise.<Object>} - API response
 */
function submitTransaction(transaction) {
    return storeXHR('POST', '/api/store_transaction/?format=json', transaction);
}

function scrollToTop() {
    $('html,body').animate({
        scrollTop: $(".store").offset().top
    }, 500);
}

Vue.filter('formatPrice', formatPrice);

/**
 * Displays a single store product with cart counts and "add" button.
 */
Vue.component('store-product', {
    template: require('!raw-loader!./store_product.html'),
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
        }
    },
    computed: {
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

/**
 * Instanssi.org store frontend application.
 */
let app = new Vue({
    el: '#store',
    data: {
        /** Current step. 0 = products, 1 = info, 2 = summary & payment */
        step: 0,
        /** Products list. */
        products: [],
        /** Current shopping cart contents. */
        cart: [],
        /** Form messages, as Object of field names to Array.<String>. */
        messages: {},
        /** Set to 'done' or 'error' based on XHR result. */
        loadingStatus: 'loading',
        /** Customer information for payment and delivery purposes. */
        info: {
            first_name: '',
            last_name: '',
            email: '',
            email2: '',
            street: '',
            postal_code: '',
            city: '',
            country: 'fi',
            mobile: '',
            telephone: '',
            company: '',
            information: '',
            read_terms: false,
        },
        /** Payment method, see PAYMENT_METHODS; default is Paytrail. */
        paymentMethod: 1,
        /** Current sum of cart item prices. */
        totalPrice: 0,
        /** True if the customer info has been validated and has not changed since then. */
        customerInfoIsValid: false,
        /** Set when purchase is ready to be paid. */
        paymentURL: null,
    },
    template: require('!raw-loader!./store.html'),
    created() {
        // fetch products list
        fetchItems().then((items) => {
            items.forEach((item) => {
                item.price = parseFloat(item.price);
            });
            this.products = items;
            this.loadingStatus = 'done';
        }).catch((e) => {
            console.error('error fetching store items:', e);
            this.loadingStatus = 'error';
        });

        // FIXME: Fetch cart from window.localstorage if it exists
    },
    computed: {
        paymentMethods() {
            return PAYMENT_METHODS;
        }
    },
    methods: {
        canMoveToStep(step) {
            let ok = true;
            if(step > 0) {
                ok = ok && this.cart.length > 0;
            }
            if(step > 1) {
                // Should we require that the user clicks the button at the bottom?
                // After that the customer info should be valid.
                // (disable the button again if the user changes their personal information)
                ok = ok && this.customerInfoIsValid;
            }
            return ok;
        },
        /**
         * Move between stages in the shopping process. May perform some validation.
         * @param {number} next - Next step to move to
         * @param {boolean} scrollUp - Should the page scroll up on successful transition?
         */
        toStep(next, scrollUp) {
            // Check form status between steps so the user doesn't have to come back later.
            if(this.step === 0) {
                // 0 -> _: check that cart contains one item
                if(this.cart.length < 1) {
                    this.messages = {
                        items: [ 'Valitse ainakin yksi tuote.' ]
                    }
                    return;
                }
                this.messages = {};
                this.step = next;

                if(scrollUp) {
                    scrollToTop();
                }
            } else if (this.step === 1 && next === 2) {
                const { info } = this;
                // 1 -> 2: send a "save=false" transaction request

                // validate email before doing anything
                if(info.email !== info.email2) {
                    this.messages = {
                        email: ['Kirjoita sama sähköpostiosoite kahdesti.'],
                        email2: ['Kirjoita sama sähköpostiosoite kahdesti.']
                    };
                    return;
                }

                // validate what the user has input so far
                let transaction = this.getTransactionObject();
                // dry run only, don't actually try to complete the transaction
                transaction.save = false;

                submitTransaction(transaction).then((res) => {
                    this.messages = {};
                    this.step = next;
                    this.customerInfoIsValid = true;

                    if(scrollUp) {
                        scrollToTop();
                    }
                }).catch((err) => {
                    this.messages = err;
                });
            } else {
                // sure, whatever
                this.messages = {};
                this.step = next;

                if(scrollUp) {
                    scrollToTop();
                }
            }
        },
        /**
         * Pick up changes to the customer information.
         */
        updateInfo() {
            // require user to click the "next step" button again
            this.customerInfoIsValid = false;
        },
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
        },
        /**
         * Update cart state, calculating total price and so on.
         */
        updateCart() {
            let totalPrice = 0;
            this.cart.forEach((cartItem) => {
                totalPrice += this.getSubtotal(cartItem);
            });
            this.totalPrice = totalPrice;
            // FIXME: Store cart in window.localStorage
        },
        /**
         * Add an item to the cart.
         * @param {Object} product - Product / StoreItem to add
         * @param {Object} [variant] - Variant to add, if any
         */
        addItem(product, variant) {
            // check if product/variant is already in items
            let found = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });
            if (found >= 0) {
                let cartItem = this.cart[found];
                this.changeItemCount(cartItem, 1);
            } else {
                // if it isn't, push a new item
                this.cart.push({
                    count: 1,
                    product: product,
                    variant: variant
                });
            }
            this.updateCart();
        },
        /**
         * Removes one item from the cart.
         * @param {Object} product - Product / StoreItem to remove
         * @param {Object} [variant] - Variant to remove, if any
         */
        removeItem(product, variant) {
            let found = this.cart.findIndex((item) => {
                return cartItemEquals(item, product, variant);
            });
            if(found >= 0) {
                this.changeItemCount(this.cart[found], -1);
            }
        },
        /**
         * Removes an existing cart item from the cart.
         * @param {Object} cartItem - Cart entry to remove
         */
        removeItemFromCart(cartItem) {
            let pos = this.cart.indexOf(cartItem);
            this.cart.splice(pos, 1);
            this.updateCart();
        },
        /**
         * Updates an item's count in the shopping cart.
         * @param {Object} item - Item to update
         * @param {number} change - Items to add (or remove)
         */
        changeItemCount(item, change) {
            // FIXME: Check item product max per order
            let pos = this.cart.indexOf(item);
            let cartItem = this.cart[pos];
            if (cartItem.count + change <= 0) {
                this.removeItemFromCart(cartItem);
                return;
            }
            cartItem.count += change;
            this.cart.splice(pos, 1, cartItem);
            this.updateCart();
        },
        /**
         * Generates an API transaction object from the store's current state.
         * @returns {Object} - Transaction to submit
         */
        getTransactionObject() {
            let transaction = Object.assign({}, this.info);
            transaction.items = this.cart.map((item) => ({
                item_id: item.product.id,
                variant_id: item.variant ? item.variant.id : null,
                amount: item.count,
            }));
            transaction.payment_method = this.paymentMethod;
            return transaction;
        },
        /**
         * Sends the current store data to the backend.
         * @returns {Promise} - Request results
         */
        submit() {
            let { info } = this;


            let transaction = this.getTransactionObject();
            // TODO: If we split this page into phases (items, info, confirm and choose method?),
            // this could be done at each step before proceeding
            transaction.save = true;

            return submitTransaction(transaction).then((res) => {
                console.info(res);
                this.paymentURL = res.url;
            }, (err) => {
                this.messages = err;
                // Manipulate error message so both email fields show errors
                if(err) {
                    err.email2 = err.email;
                }
            }).catch(err => {
                console.error(err);
            });
        }
    }
});
