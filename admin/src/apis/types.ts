// THESE TYPES SHOULD BE USED ONLY BY API -- SERVICES MUST CONVERT.

export type SocialAuthMethodsResponse = Array<{
    method: string;
    url: string;
    name: string;
}>;

export type CurrentUserInfoResponse = {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    user_permissions: string[];
    is_superuser: boolean;
};
