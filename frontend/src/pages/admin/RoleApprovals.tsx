import { useEffect, useState } from "react";
import {
  listRoleRequests,
  approveRoleRequest,
  rejectRoleRequest,
} from "../../api/roles";
import { useTranslation } from "react-i18next";
import { Spinner } from "react-bootstrap";

type RoleReq = {
  id: number;
  user_id: number;
  requested_role: string; // 'analyst' | 'manager' | ...
};

export default function RoleApprovals() {
  const { t } = useTranslation();
  const [items, setItems] = useState<RoleReq[]>([]);
  const [busy, setBusy] = useState(false);

  const load = async () => {
    setBusy(true);
    try {
      const data = await listRoleRequests("pending");
      setItems(data);
    } finally {
      setBusy(false);
    }
  };

  const act = async (id: number, action: "approve" | "reject") => {
    setBusy(true);
    try {
      if (action === "approve") await approveRoleRequest(id);
      else await rejectRoleRequest(id);
      await load();
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h4 className="mb-0">{t("admin.roleRequests.title")}</h4>
        <button
          className="btn btn-outline-primary"
          onClick={load}
          disabled={busy}
        >
          {busy ? <Spinner size="sm" /> : t("common.refresh")}
        </button>
      </div>

      <div className="table-responsive">
        <table className="table table-hover table-fixed align-middle">
          {/* фиксированные ширины колонок — предотвращают «прыжки» при смене языка */}
          <colgroup>
            <col className="col-id" />
            <col className="col-user" />
            <col className="col-role" />
            <col className="col-actions" />
          </colgroup>

          <thead>
            <tr>
              <th className="nowrap">ID</th>
              <th className="nowrap">{t("admin.roleRequests.userId")}</th>
              {/* ключ лучше назвать requestedRole, чтобы не путать со статусом/ролью пользователя */}
              <th className="nowrap">{t("admin.roleRequests.requestedRole")}</th>
              <th className="text-end nowrap">{t("common.actions")}</th>
            </tr>
          </thead>

          <tbody>
            {busy ? (
              <tr>
                <td colSpan={4} className="text-center py-4">
                  <Spinner animation="border" />
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={4} className="text-center text-muted py-4">
                  {t("admin.roleRequests.empty")}
                </td>
              </tr>
            ) : (
              items.map((it) => (
                <tr key={it.id}>
                  <td>{it.id}</td>
                  <td>{it.user_id}</td>
                  <td title={t(`roles.${it.requested_role}`, it.requested_role)}>
                    {t(`roles.${it.requested_role}`, it.requested_role)}
                  </td>
                  <td className="text-end">
                    <div className="d-inline-flex gap-2">
                      <button
                        className="btn btn-sm btn-success btn-approve"
                        onClick={() => act(it.id, "approve")}
                        disabled={busy}
                      >
                        {t("common.approve")}
                      </button>
                      <button
                        className="btn btn-sm btn-outline-danger btn-reject"
                        onClick={() => act(it.id, "reject")}
                        disabled={busy}
                      >
                        {t("common.reject")}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
