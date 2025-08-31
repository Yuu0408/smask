import { type App, markRaw, ref } from 'vue';
import DialogManagerComponent from './components/DialogManager.vue';

/*
 * Dialog Manager Plugin
 *
 * Custom utility for managing dialog components for this project.
 * This allows for more flexibity in how dialogs are opened and closed, which means it allows for more complex dialog interactions.
 *
 * Yes, I have been dealing with just dialog and forms for the past few days, that's why I made this to save my own future me sanity
 * Note that this plugin isn't coded with generic use in mind (It's quite a slightly opiniated one), the components need to have a specific structure to work with this plugin.
 * This is used to mainly deal with Shadcn UI Dialog components, edit DialogManager.vue to change how it works for other UI Library
 *
 * Usage:
 * 1. Dialog components need to have a v-model:open prop to control their open state.
 * 2. Run openDialog({ component: YourDialogComponent, props: { ... } }) to open a dialog.
 * 3. You can specify and ID for the dialog, or it will default to the current stack length. This allows for more minute control over dialogs.
 * 4. To close a dialog, use closeDialog(dialogId) or closeLatestDialog() to close the most recent dialog
 * 4.1 Alternatively, you can provide the @submit.emit signal if there is a trigger, this was mainly done to support dialog with forms in mind, it's a bit redundant but oh well :shurg:
 * 5. To close all dialogs, use closeAllDialogs().
 * 6. Close dialog allows you to pass the result into the promise that is used to open the dialog, use it to return data from openDialog.
 *
 * Bonus: Oh yeah, Dialog can stacks, Seem like unintended feature lol, hence why closeLatestDialog() is provided. Have fun with it
 */

type DialogStackItem = {
    id: string;
    component: any;
    props?: Record<string, any>;
    isOpen: boolean;
    resolve?: (value: any) => void;
    reject?: (reason?: any) => void;
};

type DialogOptions = {
    component: any;
    id?: string; // Optional ID
    props?: Record<string, any>;
};

const dialogStack = ref<DialogStackItem[]>([]);

const openDialog = <T = any>(options: DialogOptions) => {
    return new Promise<T>((resolve, reject) => {
        const id = options.id ?? dialogStack.value.length.toString();
        dialogStack.value.push({
            id,
            component: markRaw(options.component),
            props: options.props || {},
            isOpen: true,
            resolve,
            reject,
        });
    });
};

const closeDialog = (dialogId: string, result?: any) => {
    const index = dialogStack.value.findIndex((d) => d.id === dialogId);
    if (index !== -1) {
        const dialog = dialogStack.value[index];
        dialog.resolve?.(result);
        dialogStack.value.splice(index, 1);
    }
};

const closeLatestDialog = (result?: any) => {
    if (dialogStack.value.length > 0) {
        const latestDialog = dialogStack.value[dialogStack.value.length - 1];
        closeDialog(latestDialog.id, result);
    }
};

const closeAllDialogs = () => {
    dialogStack.value.forEach((dialog) => {
        dialog.reject?.('Dialog closed');
    });
    dialogStack.value = [];
};

const handleOpenChange = (dialogId: string, isOpen: boolean) => {
    if (!isOpen) {
        closeDialog(dialogId);
    }
};

export const dialogUtils = {
    dialogStack,
    openDialog,
    closeDialog,
    closeLatestDialog,
    closeAllDialogs,
    handleOpenChange,
};

export default {
    install(app: App) {
        app.component('DialogManager', DialogManagerComponent);

        app.provide('openDialog', openDialog);
        app.provide('closeDialog', closeDialog);
        app.provide('closeLatestDialog', closeLatestDialog);
        app.provide('closeAllDialogs', closeAllDialogs);
    },
};
