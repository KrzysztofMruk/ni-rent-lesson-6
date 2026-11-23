from src.manager import Manager
from src.models import Parameters


def test_tenants_settlement_totals_match_apartment_costs():
    manager = Manager(Parameters())
    apartment_key = 'apart-polanka'
    year = 2025
    month = 1

    apartment_settlement = manager.get_settlement(apartment_key, year, month)
    tenants_settlements = manager.create_tenants_settlements(apartment_settlement)

    total_tenant_due = sum(
        tenant_settlement.total_due_pln
        for tenant_settlement in tenants_settlements
    )
    apartment_costs = manager.get_apartment_costs(apartment_key, year, month)

    assert total_tenant_due == apartment_costs


def test_financial_report_shows_costs_payments_and_balances():
    manager = Manager(Parameters())

    report = manager.get_financial_report('apart-polanka', 2025, 1)

    assert report['total_costs_pln'] == 910.0
    assert report['total_transfers_pln'] == 7500.0
    assert report['balance_pln'] == 6590.0
    assert len(report['tenants']) == 3
    assert all(tenant['total_transfers_pln'] == 2500.0 for tenant in report['tenants'])
    assert all(tenant['balance_pln'] == 2500.0 - 910.0 / 3 for tenant in report['tenants'])


def test_get_debtors_returns_tenants_who_paid_less_than_rent():
    manager = Manager(Parameters())

    debtors = manager.get_debtors('apart-polanka', 1, 2025)

    assert debtors == []

    # Payments in January 2025 exceed rent; with no transfers in the next
    # period, all tenants in the apartment are debtors.
    debtors = manager.get_debtors('apart-polanka', 2, 2025)

    assert {tenant.name for tenant in debtors} == {
        'Jan Nowak',
        'Adam Kowalski',
        'Ewa Adamska',
    }
