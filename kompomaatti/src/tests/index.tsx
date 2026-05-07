import { render } from '@testing-library/react';
import React from 'react';
import { BrowserRouter, StaticRouter } from 'react-router-dom';

export * from './mocks';

/**
 * Wrap something in this to provide common dependencies.
 */
export const TestWrapper: React.FC<{ children?: React.ReactNode, routerArgs?: { location?: string } }> = ({ children, routerArgs }) => {
    return <StaticRouter {...routerArgs}>{children}</StaticRouter>
};

/**
 * Render test content using this to automatically wrap it in various context providers.
 */
export const testRender = (content: React.ReactNode, routerArgs?: { location?: string }) => {
    return render(<TestWrapper routerArgs={routerArgs}>{content}</TestWrapper>);
};
