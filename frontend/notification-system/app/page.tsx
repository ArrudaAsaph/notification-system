export default function Home() {
  return (
    <section className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Notificações</h2>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            Acompanhe mensagens enviadas pelos consumidores (email, admin, pedidos).
          </p>
        </div>
        <div className="flex gap-2">
          <button className="rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm hover:bg-zinc-50 dark:border-zinc-700 dark:bg-zinc-900 dark:hover:bg-zinc-800">
            Atualizar
          </button>
          <button className="rounded-md bg-zinc-900 px-3 py-2 text-sm text-white hover:bg-zinc-800 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-200">
            Configurações
          </button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <h3 className="font-medium">Fila Email</h3>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">Último envio: —</p>
        </div>
        <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <h3 className="font-medium">Fila Admin</h3>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">Última ação: —</p>
        </div>
        <div className="rounded-lg border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
          <h3 className="font-medium">Fila Pedidos</h3>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">Último pedido: —</p>
        </div>
      </div>

      <div className="rounded-lg border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-900">
        <div className="border-b border-zinc-200 px-4 py-3 dark:border-zinc-800">
          <h3 className="text-sm font-medium">Atividade recente</h3>
        </div>
        <ul className="divide-y divide-zinc-200 dark:divide-zinc-800">
          {[1, 2, 3, 4].map((i) => (
            <li key={i} className="px-4 py-3 text-sm">
              Mensagem #{i} — aguardando integração com API Gateway.
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
