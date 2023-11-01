Adicionar Traço
---------------

A tela de adição de traço permite o preenchimento dos seguintes campos:

    - Nome
        Tipo: Obrigatório

        Descrição: Nome do traço

    - Porcentagem de água
        Tipo: Obrigatório

        Descrição: Porcentagem de água que compõe o volume do traço, deve ser um número real entre 0 e 100

    - Descrição
        Tipo: Opcional

        Descrição: Descrição do traço

    **Agregados**

        Lista contendo todos os 'Tipos de Agregados' cadastrados.

        Para cada tipo de agregado, pode-se selecionar um agregado, cadastrado previamente.

        Caso um agregado tenha sido selecionado, é necessário preencher a 'Porcentagem Agregado'

        - Agregado
            Tipo: Opcional

            Descrição: Nome do agregado


        - Porcentagem Agregado:

            Tipo: Obrigatório caso agregado foi selecionado

            Descrição: Porcentagem do agregado no **volume** do traço. Deve ser um valor real entre 0 e 100.

    .. warning::

        A soma das porcentagens do agregados com a porcentagem de água deve ser igual a 100.