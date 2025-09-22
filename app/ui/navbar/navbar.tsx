"use client";

import Link from "next/link";
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/react'
import Image from 'next/image';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx';
import { NavigationItem } from '@/app/lib/definitions';
import { Button } from "@/app/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/app/ui/navbar/dropdown-menu";
import { appConfig } from "@/app/app.config";
import { useTranslation } from 'react-i18next';
import ThemeToggle from "@/app/ui/navbar/theme-toggle";
import LanguageToggle from "@/app/ui/navbar/language-toggle";
// import { useAuthenticator } from '@aws-amplify/ui-react';
// import { useRouter } from 'next/navigation';
import './navbar.css';

const Navbar = () => {
    const { t } = useTranslation('common');
    // const { user, signOut } = useAuthenticator();
    // const router = useRouter();

    // const handleSignIn = () => {
    //     router.push('/signin');
    // };

    // const handleSignUp = () => {
    //     router.push('/signup');
    // };

    // const handleSignOut = () => {
    //     signOut();
    // };

    const navigation: NavigationItem[] = [
        { name: t('navHome'), href: '/', current: true },
        { name: t('navDashboard'), href: '/dashboard', current: false, subLinks: [
            { name: t('navProjects'), href: '/dashboard' },
            { name: t('navGrowthCurves'), href: '/dashboard/growth' },
        ]},
        { name: t('navUpload'), href: '/upload', current: false },
        { name: t('navConnect'), href: '/connect', current: false },
    ];

    function classNames(...classes: (string | boolean | undefined)[]): string {
        return classes.filter(Boolean).join(' ');
    }

    return (
        <Disclosure as="nav" className="bg-logo-deep shadow-md">
            {({ open }) => (
                <>
                    <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
                        <div className="relative flex h-16 items-center justify-between">
                            <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
                                <DisclosureButton className="group relative inline-flex items-center justify-center rounded-md p-2 navbar-text-muted hover:bg-logo-mid hover:text-white focus:outline-none focus:ring-2 focus:ring-logo-light">
                                    <span className="sr-only">Open main menu</span>
                                    {open ? (
                                        <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                                    ) : (
                                        <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                                    )}
                                </DisclosureButton>
                            </div>
                            <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
                                <Link href="/" className="flex flex-shrink-0 items-center">
                                    <Image
                                        src={appConfig.logo.path}
                                        alt={appConfig.logo.alt}
                                        width={32}
                                        height={32}
                                        style={{
                                            height: "2rem",
                                            width: "auto",
                                            marginRight: "0.5rem",
                                        }}
                                    />
                                    <div className="flex items-center">
                                        <span className="hidden sm:inline navbar-text font-medium">
                                            {t('navTitle')}
                                        </span>
                                    </div>
                                </Link>
                                
                                <div className="hidden sm:ml-6 sm:block">
                                    <div className="flex space-x-1">
                                        {navigation.map((link) => (
                                            link.subLinks ? (
                                                <DropdownMenu key={link.name}>
                                                    <DropdownMenuTrigger asChild>
                                                        <Button variant="ghost" className={clsx(
                                                            "navbar-text-muted hover:bg-logo-mid hover:text-white rounded-md px-3 py-2 text-sm font-medium",
                                                            {
                                                                'bg-logo-mid navbar-text': link.current,
                                                            })}
                                                        >
                                                            {link.name}
                                                        </Button>
                                                    </DropdownMenuTrigger>
                                                    <DropdownMenuContent align="start" className="navbar-dropdown">
                                                        {link.subLinks.map((subLink) => (
                                                            <DropdownMenuItem key={subLink.name} asChild className="hover:bg-logo-light/10">
                                                                <Link href={subLink.href}>
                                                                    {subLink.name}
                                                                </Link>
                                                            </DropdownMenuItem>
                                                        ))}
                                                    </DropdownMenuContent>
                                                </DropdownMenu>
                                            ) : (
                                                <Link
                                                    key={link.name}
                                                    href={link.href}
                                                    className={clsx(
                                                        "navbar-text-muted hover:bg-logo-mid hover:text-white rounded-md px-3 py-2 text-sm font-medium",
                                                        {
                                                            'bg-logo-mid navbar-text': link.current,
                                                        })}
                                                >
                                                    {link.name}
                                                </Link>
                                            )
                                        ))}
                                    </div>
                                </div>
                            </div>
                            
                            <div className="flex items-center justify-center sm:items-stretch sm:justify-start">
                                <p className="navbar-text-muted hidden md:block mx-4 text-sm">
                                    {t('navTagline')}
                                </p>
                            </div>
                            
                            <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0 px-6">
                                <ThemeToggle />
                                <LanguageToggle />
                                {/* <div className="flex items-center space-x-2 pl-4">
                                    {!user ? (
                                        <>
                                            <button
                                                onClick={handleSignIn}
                                                className="navbar-text-muted hover:bg-logo-mid hover:text-white rounded-md px-3 py-2 text-sm font-medium"
                                            >
                                                {t('navLogin')}
                                            </button>
                                            <button
                                                onClick={handleSignUp}
                                                className="navbar-text-muted hover:bg-logo-mid hover:text-white rounded-md px-3 py-2 text-sm font-medium"
                                            >
                                                {t('navSignup')}
                                            </button>
                                        </>
                                    ) : (
                                        <button
                                            onClick={handleSignOut}
                                            className="navbar-text-muted hover:bg-logo-mid hover:text-white rounded-md px-3 py-2 text-sm font-medium"
                                        >
                                            {t('navLogout') || 'Sign Out'}
                                        </button>
                                    )}
                                </div> */}
                            </div>
                        </div>
                    </div>
                    
                    <DisclosurePanel className="sm:hidden">
                        <div className="space-y-1 px-2 pt-2 pb-3">
                            {navigation.map((item) => (
                                item.subLinks ? (
                                    <div key={item.name} className="border-l-2 border-logo-light/40">
                                        <DisclosureButton
                                            as="div"
                                            className="block rounded-md px-3 py-2 text-base font-medium navbar-text-muted hover:bg-logo-mid hover:text-white"
                                        >
                                            {item.name}
                                        </DisclosureButton>
                                        <div className="pl-4">
                                            {item.subLinks.map((subLink) => (
                                                <DisclosureButton
                                                    key={subLink.name}
                                                    as="a"
                                                    href={subLink.href}
                                                    className="block rounded-md px-3 py-2 text-sm font-medium navbar-text-muted hover:bg-logo-mid hover:text-white"
                                                >
                                                    {subLink.name}
                                                </DisclosureButton>
                                            ))}
                                        </div>
                                    </div>
                                ) : (
                                    <DisclosureButton
                                        key={item.name}
                                        as="a"
                                        href={item.href}
                                        aria-current={item.current ? 'page' : undefined}
                                        className={classNames(
                                            item.current ? 'bg-logo-mid navbar-text' : 'navbar-text-muted hover:bg-logo-mid hover:text-white',
                                            'block rounded-md px-3 py-2 text-base font-medium',
                                        )}
                                    >
                                        {item.name}
                                    </DisclosureButton>
                                )
                            ))}
                        </div>
                    </DisclosurePanel>
                </>
            )}
        </Disclosure>
    );
};

export default Navbar;