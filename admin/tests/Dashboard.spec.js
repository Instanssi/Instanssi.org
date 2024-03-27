import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import DashBoard from '@/views/MainView.vue'

describe('DashBoard', () => {
  it('renders properly', () => {
    const wrapper = mount(DashBoard, { props: {} })
    expect(wrapper.text()).toContain('MainView.title')
  });
});
