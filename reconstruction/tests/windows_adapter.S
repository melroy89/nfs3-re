.intel_syntax noprefix
.text
.globl _nfs3_call_original
.def _nfs3_call_original; .scl 2; .type 32; .endef
_nfs3_call_original:
    push ebp
    push ebx
    push esi
    push edi
    mov ebp, [esp + 20]       /* function entry */
    mov eax, [esp + 24]       /* candidate */
    mov edx, [esp + 28]       /* source line */
    mov ebx, [esp + 32]       /* bounds */
    mov ecx, [esp + 36]       /* return policy */
    mov edi, [esp + 40]       /* mask */
    push edi
    call ebp
    mov edi, [esp + 48]       /* result */
    mov [edi + 20], eax       /* diagnostic: actual original return pointer */
    test eax, eax
    jz .Lnull_return
    mov edx, [esp + 44]       /* private scratch base */
    add edx, 0x1c08
    cmp eax, edx
    jne .Lbad_return
    mov dword ptr [edi], 1    /* shared result storage class */
    jmp .Lreturn_saved
.Lnull_return:
    mov dword ptr [edi], 0
    jmp .Lreturn_saved
.Lbad_return:
    mov dword ptr [edi], 2
.Lreturn_saved:
    mov edx, [esp + 44]
    mov eax, dword ptr [edx + 0x1c08]
    mov [edi + 4], eax
    mov eax, dword ptr [edx + 0x1c0c]
    mov [edi + 8], eax
    mov edx, [esp + 40]
    movzx eax, byte ptr [edx]
    mov [edi + 12], eax
    fnstcw word ptr [edi + 16]
    fnstsw ax
    mov [edi + 18], ax
    pop edi
    pop esi
    pop ebx
    pop ebp
    ret
